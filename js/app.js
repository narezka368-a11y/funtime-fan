/* FunTime fan site — interaction layer (no dependencies) */
(() => {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /* ---------------------------------------------------------
     Header: shadow on scroll + reading progress bar
     --------------------------------------------------------- */
  const header = $("#siteHeader");
  const progress = $("#progress");

  const onScroll = () => {
    const y = window.scrollY;
    if (header) header.classList.toggle("is-scrolled", y > 8);
    if (progress) {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.width = max > 0 ? `${Math.min(100, (y / max) * 100)}%` : "0%";
    }
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------------------------------------------------------
     Mobile navigation
     --------------------------------------------------------- */
  const burger = $("#burger");
  const nav = $("#nav");

  const setNav = (open) => {
    if (!nav || !burger) return;
    nav.classList.toggle("is-open", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.setAttribute("aria-label", open ? "Закрыть меню" : "Открыть меню");
  };

  if (burger && nav) {
    burger.addEventListener("click", () => setNav(!nav.classList.contains("is-open")));

    nav.addEventListener("click", (e) => {
      if (e.target.closest("a")) setNav(false);
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        setNav(false);
        burger.focus();
      }
    });

    document.addEventListener("click", (e) => {
      if (!nav.contains(e.target) && !burger.contains(e.target)) setNav(false);
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 860) setNav(false);
    });
  }

  /* ---------------------------------------------------------
     Copy-to-clipboard + toast
     --------------------------------------------------------- */
  const toast = $("#toast");
  let toastTimer = null;

  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 2200);
  };

  const copyText = async (text) => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch {
      /* fall through to the legacy path */
    }
    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.cssText = "position:fixed;top:-9999px;opacity:0";
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(ta);
      return ok;
    } catch {
      return false;
    }
  };

  document.addEventListener("click", async (e) => {
    const trigger = e.target.closest("[data-copy]");
    if (!trigger) return;
    const value = trigger.getAttribute("data-copy");
    const ok = await copyText(value);
    showToast(ok ? `IP ${value} скопирован — вставляй в Minecraft` : `Не вышло скопировать. Адрес: ${value}`);
  });

  /* ---------------------------------------------------------
     Reveal sections on scroll
     --------------------------------------------------------- */
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!reduceMotion && "IntersectionObserver" in window) {
    const candidates = $$(
      ".strip__item, .about__text > *, .about__card, .mode, .shot, .step, .guide, .faq__item, .connect__panel, .section__head"
    );
    // Only hide what is still below the fold, so nothing ever flashes empty.
    const targets = candidates.filter(
      (el) => el.getBoundingClientRect().top > window.innerHeight * 0.9
    );
    targets.forEach((el, i) => el.classList.add("reveal", `reveal--d${i % 4}`));

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-in");
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    targets.forEach((el) => io.observe(el));

    // Safety net: never leave content invisible if the observer stays silent.
    window.setTimeout(() => {
      $$(".reveal:not(.is-in)").forEach((el) => el.classList.add("is-in"));
    }, 3000);
  }

  /* ---------------------------------------------------------
     Active nav link
     --------------------------------------------------------- */
  const navLinks = $$(".nav__link[href^='#']");
  const sections = navLinks
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

  if ("IntersectionObserver" in window && sections.length) {
    const spy = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          navLinks.forEach((link) =>
            link.classList.toggle("is-active", link.getAttribute("href") === `#${entry.target.id}`)
          );
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach((section) => spy.observe(section));
  } else if (navLinks.length) {
    navLinks[0].classList.add("is-active");
  }

  /* ---------------------------------------------------------
     Guides: keep only one open at a time
     --------------------------------------------------------- */
  const guides = $$(".guide");
  guides.forEach((guide) => {
    guide.addEventListener("toggle", () => {
      if (!guide.open) return;
      guides.forEach((other) => {
        if (other !== guide) other.open = false;
      });
    });
  });

  /* ---------------------------------------------------------
     Gallery lightbox
     --------------------------------------------------------- */
  const lightbox = $("#lightbox");
  const lightboxImg = $("#lightboxImg");
  const lightboxCap = $("#lightboxCap");
  const shots = $$(".shot__btn");
  let currentShot = 0;
  let lastFocus = null;

  if (lightbox && lightboxImg && shots.length) {
    const render = (index) => {
      currentShot = (index + shots.length) % shots.length;
      const btn = shots[currentShot];
      const thumb = btn.querySelector("img");
      lightboxImg.src = btn.dataset.full || (thumb ? thumb.src : "");
      lightboxImg.alt = thumb ? thumb.alt : "";
      if (lightboxCap) lightboxCap.textContent = btn.dataset.caption || "";
    };

    const closeLightbox = () => {
      lightbox.hidden = true;
      document.body.style.overflow = "";
      if (lastFocus) lastFocus.focus();
    };

    const openLightbox = (index) => {
      lastFocus = document.activeElement;
      render(index);
      lightbox.hidden = false;
      document.body.style.overflow = "hidden";
      const closeBtn = lightbox.querySelector(".lightbox__close");
      if (closeBtn) closeBtn.focus();
    };

    shots.forEach((btn, i) => btn.addEventListener("click", () => openLightbox(i)));

    lightbox.addEventListener("click", (e) => {
      if (e.target === lightbox || e.target.closest(".lightbox__close")) {
        closeLightbox();
        return;
      }
      const nav = e.target.closest("[data-step]");
      if (nav) {
        render(currentShot + Number(nav.dataset.step));
        lastFocus = shots[currentShot];
      }
    });

    document.addEventListener("keydown", (e) => {
      if (lightbox.hidden) return;
      if (e.key === "Escape") {
        closeLightbox();
      } else if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        render(currentShot + (e.key === "ArrowLeft" ? -1 : 1));
        lastFocus = shots[currentShot];
      }
    });
  }

  /* ---------------------------------------------------------
     Small nicety: current year in the footer-free zone
     --------------------------------------------------------- */
  const yearEl = document.querySelector("[data-year]");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());
})();
