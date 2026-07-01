(() => {
  "use strict";

  const state = {
    slides: [],
    activeSlideId: null,
    selectedFindingId: null,
    zoom: "fit",
    draftRect: null,
  };

  const $ = (id) => document.getElementById(id);
  const elements = {
    slideFiles: $("slide-files"),
    importJson: $("import-json"),
    exportJson: $("export-json"),
    thumbnailList: $("thumbnail-list"),
    emptySlides: $("empty-slides"),
    slideCount: $("slide-count"),
    findingCount: $("finding-count"),
    activeSlideTitle: $("active-slide-title"),
    activeSlideMeta: $("active-slide-meta"),
    stage: $("slide-stage"),
    image: $("slide-image"),
    svg: $("overlay-svg"),
    overlayRectangles: $("overlay-rectangles"),
    form: $("review-form"),
    severity: $("severity"),
    category: $("category"),
    comment: $("comment"),
    suggestedFix: $("suggested_fix"),
    deleteFinding: $("delete-finding"),
    clearSlideFindings: $("clear-slide-findings"),
    findingList: $("finding-list"),
    emptyFindings: $("empty-findings"),
    statusLine: $("status-line"),
    fitSlide: $("fit-slide"),
    actualSize: $("actual-size"),
  };

  const severityAliases = { minor: "low", major: "high", warning: "medium", error: "high" };
  const validSeverities = new Set(["info", "low", "medium", "high", "critical"]);

  function normalizeSeverity(value) {
    const lowered = String(value || "info").trim().toLowerCase();
    const normalized = severityAliases[lowered] || lowered || "info";
    return validSeverities.has(normalized) ? normalized : "info";
  }

  function rectToRoi(rect) {
    return { x: rect.x, y: rect.y, w: rect.width, h: rect.height };
  }

  function uid(prefix) {
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  }

  function naturalSlideSort(a, b) {
    return a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: "base" });
  }

  function activeSlide() {
    return state.slides.find((slide) => slide.id === state.activeSlideId) || null;
  }

  function selectedFinding() {
    const slide = activeSlide();
    if (!slide) return null;
    return slide.findings.find((finding) => finding.id === state.selectedFindingId) || null;
  }

  function setStatus(message) {
    elements.statusLine.textContent = message;
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function normalizeRect(rect) {
    const x = Math.min(rect.x, rect.x + rect.width);
    const y = Math.min(rect.y, rect.y + rect.height);
    return {
      x: clamp(x, 0, 1),
      y: clamp(y, 0, 1),
      width: clamp(Math.abs(rect.width), 0, 1 - clamp(x, 0, 1)),
      height: clamp(Math.abs(rect.height), 0, 1 - clamp(y, 0, 1)),
    };
  }

  function validateImportedRect(rect) {
    if (!rect || typeof rect !== "object") throw new Error("finding rectangle is missing");
    const candidate = {
      x: Number(rect.x),
      y: Number(rect.y),
      width: Number(rect.width ?? rect.w),
      height: Number(rect.height ?? rect.h),
    };
    for (const [key, value] of Object.entries(candidate)) {
      if (!Number.isFinite(value)) throw new Error(`finding rectangle ${key} must be numeric`);
      if (value < 0 || value > 1) throw new Error(`finding rectangle ${key} must be between 0 and 1`);
    }
    if (candidate.width <= 0 || candidate.height <= 0) throw new Error("finding rectangle width and height must be greater than zero");
    if (candidate.x + candidate.width > 1 || candidate.y + candidate.height > 1) {
      throw new Error("finding rectangle must stay within normalized slide bounds");
    }
    return candidate;
  }

  function imageDisplayBox() {
    const stageRect = elements.stage.getBoundingClientRect();
    const imageRect = elements.image.getBoundingClientRect();
    if (!imageRect.width || !imageRect.height) return null;
    return {
      left: imageRect.left - stageRect.left + elements.stage.scrollLeft,
      top: imageRect.top - stageRect.top + elements.stage.scrollTop,
      width: imageRect.width,
      height: imageRect.height,
    };
  }

  function pointToNormalized(event) {
    const box = imageDisplayBox();
    if (!box) return null;
    const stageRect = elements.stage.getBoundingClientRect();
    const x = (event.clientX - stageRect.left + elements.stage.scrollLeft - box.left) / box.width;
    const y = (event.clientY - stageRect.top + elements.stage.scrollTop - box.top) / box.height;
    return { x: clamp(x, 0, 1), y: clamp(y, 0, 1) };
  }

  function positionOverlay() {
    const box = imageDisplayBox();
    if (!box) return;
    elements.svg.style.left = `${box.left}px`;
    elements.svg.style.top = `${box.top}px`;
    elements.svg.setAttribute("width", String(box.width));
    elements.svg.setAttribute("height", String(box.height));
    elements.svg.setAttribute("viewBox", `0 0 ${box.width} ${box.height}`);
    renderOverlay();
  }

  function applyZoom() {
    const slide = activeSlide();
    if (!slide) return;
    if (state.zoom === "actual") {
      elements.image.style.width = `${slide.width}px`;
      elements.image.style.maxWidth = "none";
    } else {
      elements.image.style.width = "auto";
      elements.image.style.maxWidth = "100%";
    }
    window.requestAnimationFrame(positionOverlay);
  }

  function loadSlides(files) {
    const pngFiles = Array.from(files || []).filter((file) => file.type === "image/png" || file.name.toLowerCase().endsWith(".png"));
    if (!pngFiles.length) {
      setStatus("No PNG files selected.");
      return;
    }

    for (const slide of state.slides) {
      URL.revokeObjectURL(slide.url);
    }

    state.slides = pngFiles.map((file, index) => ({
      id: uid("slide"),
      name: file.name,
      index: index + 1,
      url: URL.createObjectURL(file),
      width: 0,
      height: 0,
      findings: [],
    })).sort(naturalSlideSort).map((slide, index) => ({ ...slide, index: index + 1 }));

    state.activeSlideId = state.slides[0].id;
    state.selectedFindingId = null;
    hydrateImageSizes();
    render();
    setStatus(`Loaded ${state.slides.length} slide PNG file(s).`);
  }

  function hydrateImageSizes() {
    for (const slide of state.slides) {
      const img = new Image();
      img.onload = () => {
        slide.width = img.naturalWidth;
        slide.height = img.naturalHeight;
        if (slide.id === state.activeSlideId) renderActiveSlide();
        renderThumbnails();
      };
      img.src = slide.url;
    }
  }

  function render() {
    renderThumbnails();
    renderActiveSlide();
    renderFindings();
    renderForm();
  }

  function renderThumbnails() {
    elements.thumbnailList.textContent = "";
    elements.slideCount.textContent = `${state.slides.length} loaded`;
    elements.emptySlides.hidden = state.slides.length > 0;

    state.slides.forEach((slide) => {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = `thumbnail${slide.id === state.activeSlideId ? " active" : ""}`;
      button.addEventListener("click", () => selectSlide(slide.id));

      const img = document.createElement("img");
      img.src = slide.url;
      img.alt = `Thumbnail for ${slide.name}`;
      const title = document.createElement("span");
      title.className = "thumbnail-title";
      title.textContent = `Slide ${slide.index}`;
      const meta = document.createElement("span");
      meta.className = "thumbnail-meta";
      const size = slide.width && slide.height ? ` · ${slide.width}×${slide.height}` : "";
      meta.textContent = `${slide.name}${size} · ${slide.findings.length} finding(s)`;

      button.append(img, title, meta);
      item.append(button);
      elements.thumbnailList.append(item);
    });
  }

  function renderActiveSlide() {
    const slide = activeSlide();
    if (!slide) {
      elements.stage.classList.remove("has-slide");
      elements.image.removeAttribute("src");
      elements.activeSlideTitle.textContent = "No slide selected";
      elements.activeSlideMeta.textContent = "Load PNGs to begin review.";
      elements.overlayRectangles.textContent = "";
      return;
    }
    elements.stage.classList.add("has-slide");
    if (elements.image.src !== slide.url) {
      elements.image.src = slide.url;
    }
    elements.activeSlideTitle.textContent = `Slide ${slide.index}: ${slide.name}`;
    elements.activeSlideMeta.textContent = slide.width && slide.height
      ? `${slide.width}×${slide.height}px · ${slide.findings.length} finding(s)`
      : `${slide.findings.length} finding(s)`;
    applyZoom();
  }

  function rectToSvgAttrs(rect, box) {
    return {
      x: rect.x * box.width,
      y: rect.y * box.height,
      width: rect.width * box.width,
      height: rect.height * box.height,
    };
  }

  function renderOverlay() {
    const slide = activeSlide();
    const box = imageDisplayBox();
    elements.overlayRectangles.textContent = "";
    if (!slide || !box) return;

    const allRects = [...slide.findings];
    if (state.draftRect) {
      allRects.push({
        id: "draft",
        severity: "info",
        rect: normalizeRect(state.draftRect),
      });
    }

    for (const finding of allRects) {
      const attrs = rectToSvgAttrs(finding.rect, box);
      if (attrs.width < 1 || attrs.height < 1) continue;
      const rect = document.createElementNS(elements.svg.namespaceURI, "rect");
      rect.classList.add("finding-rect");
      if (finding.id === state.selectedFindingId || finding.id === "draft") rect.classList.add("selected");
      rect.dataset.findingId = finding.id;
      rect.dataset.severity = finding.severity || "info";
      rect.setAttribute("x", String(attrs.x));
      rect.setAttribute("y", String(attrs.y));
      rect.setAttribute("width", String(attrs.width));
      rect.setAttribute("height", String(attrs.height));
      rect.setAttribute("rx", "4");
      rect.setAttribute("tabindex", "0");
      rect.setAttribute("role", "button");
      rect.setAttribute("aria-label", `Finding ${finding.id}`);
      rect.addEventListener("click", (event) => {
        event.stopPropagation();
        if (finding.id !== "draft") selectFinding(finding.id);
      });
      elements.overlayRectangles.append(rect);
    }
  }

  function renderFindings() {
    const slide = activeSlide();
    const findings = slide ? slide.findings : [];
    elements.findingCount.textContent = `${state.slides.reduce((count, item) => count + item.findings.length, 0)} findings`;
    elements.findingList.textContent = "";
    elements.emptyFindings.hidden = findings.length > 0;

    findings.forEach((finding, index) => {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = `finding-item${finding.id === state.selectedFindingId ? " active" : ""}`;
      button.addEventListener("click", () => selectFinding(finding.id));
      const title = document.createElement("span");
      title.className = "finding-title";
      title.textContent = `${index + 1}. ${finding.severity || "info"} · ${finding.category || "uncategorized"}`;
      const meta = document.createElement("span");
      meta.className = "finding-meta";
      meta.textContent = finding.comment || "No comment yet";
      button.append(title, meta);
      item.append(button);
      elements.findingList.append(item);
    });
  }

  function renderForm() {
    const finding = selectedFinding();
    const disabled = !finding;
    elements.severity.value = finding?.severity || "info";
    elements.category.value = finding?.category || "";
    elements.comment.value = finding?.comment || "";
    elements.suggestedFix.value = finding?.suggested_fix || "";
    for (const control of [elements.severity, elements.category, elements.comment, elements.suggestedFix, elements.deleteFinding]) {
      control.disabled = disabled;
    }
  }

  function selectSlide(slideId) {
    state.activeSlideId = slideId;
    const slide = activeSlide();
    state.selectedFindingId = slide?.findings[0]?.id || null;
    state.draftRect = null;
    render();
  }

  function selectFinding(findingId) {
    state.selectedFindingId = findingId;
    renderFindings();
    renderForm();
    renderOverlay();
  }

  function addFinding(rect) {
    const slide = activeSlide();
    if (!slide) return null;
    const finding = {
      id: uid("finding"),
      severity: "info",
      category: "",
      comment: "",
      suggested_fix: "",
      rect: normalizeRect(rect),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    slide.findings.push(finding);
    state.selectedFindingId = finding.id;
    render();
    setStatus("Created a finding rectangle. Fill in the review fields and save.");
    return finding;
  }

  function saveFinding(event) {
    event.preventDefault();
    const finding = selectedFinding();
    if (!finding) return;
    finding.severity = normalizeSeverity(elements.severity.value);
    finding.category = elements.category.value.trim();
    finding.comment = elements.comment.value.trim();
    finding.suggested_fix = elements.suggestedFix.value.trim();
    finding.updated_at = new Date().toISOString();
    render();
    setStatus("Finding saved.");
  }

  function deleteSelectedFinding() {
    const slide = activeSlide();
    if (!slide || !state.selectedFindingId) return;
    const index = slide.findings.findIndex((finding) => finding.id === state.selectedFindingId);
    if (index >= 0) slide.findings.splice(index, 1);
    state.selectedFindingId = slide.findings[Math.max(0, index - 1)]?.id || slide.findings[0]?.id || null;
    render();
    setStatus("Finding deleted.");
  }

  function clearSlideFindings() {
    const slide = activeSlide();
    if (!slide || slide.findings.length === 0) return;
    if (!window.confirm(`Clear ${slide.findings.length} finding(s) from ${slide.name}?`)) return;
    slide.findings = [];
    state.selectedFindingId = null;
    render();
    setStatus("Cleared findings for the current slide.");
  }

  function exportPayload() {
    const slides = state.slides.map((slide) => ({
      id: slide.id,
      index: slide.index,
      name: slide.name,
      width: slide.width,
      height: slide.height,
      findings: slide.findings.map((finding) => ({
        ...finding,
        severity: normalizeSeverity(finding.severity),
        rect: { ...finding.rect },
      })),
    }));
    const comments = slides.flatMap((slide) => slide.findings.map((finding) => ({
      id: finding.id,
      slide: slide.index,
      severity: normalizeSeverity(finding.severity),
      category: finding.category || "general",
      comment: finding.comment || "Untitled finding",
      suggested_fix: finding.suggested_fix || "",
      status: "open",
      roi: rectToRoi(finding.rect),
      created_at: finding.created_at,
    })));
    return {
      schema: "ppt_slide_png_review.v1",
      generated_at: new Date().toISOString(),
      comments,
      slides,
    };
  }

  function downloadJson() {
    const payload = exportPayload();
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    const stamp = new Date().toISOString().replace(/[:.]/g, "-");
    anchor.href = url;
    anchor.download = `ppt-slide-review-${stamp}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
    setStatus("Exported review JSON.");
  }

  function importReviewJson(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const payload = JSON.parse(String(reader.result || "{}"));
        const incomingSlides = Array.isArray(payload.slides) ? payload.slides : [];
        const comments = Array.isArray(payload.comments) ? payload.comments : [];
        const importedBySlide = new Map();
        let imported = 0;
        for (const slide of state.slides) {
          const bySlide = comments.filter((comment) => Number(comment.slide || comment.slide_number || comment.page) === slide.index);
          if (bySlide.length > 0) {
            const findings = bySlide.map((comment) => ({
              id: comment.id || uid("finding"),
              severity: normalizeSeverity(comment.severity),
              category: comment.category || "",
              comment: comment.comment || comment.text || comment.body || "",
              suggested_fix: comment.suggested_fix || comment.suggestedFix || comment.suggestion || "",
              rect: validateImportedRect({
                x: comment.roi?.x ?? comment.region?.x,
                y: comment.roi?.y ?? comment.region?.y,
                width: comment.roi?.w ?? comment.roi?.width ?? comment.region?.w ?? comment.region?.width,
                height: comment.roi?.h ?? comment.roi?.height ?? comment.region?.h ?? comment.region?.height,
              }),
              created_at: comment.created_at || new Date().toISOString(),
              updated_at: comment.updated_at || new Date().toISOString(),
            }));
            importedBySlide.set(slide.id, findings);
            imported += findings.length;
          }
        }
        for (const incoming of incomingSlides) {
          const slide = state.slides.find((candidate) => candidate.name === incoming.name || candidate.index === incoming.index);
          if (!slide || !Array.isArray(incoming.findings) || importedBySlide.has(slide.id)) continue;
          const findings = incoming.findings.map((finding) => ({
            id: finding.id || uid("finding"),
            severity: normalizeSeverity(finding.severity),
            category: finding.category || "",
            comment: finding.comment || "",
            suggested_fix: finding.suggested_fix || finding.suggestedFix || "",
            rect: validateImportedRect(finding.rect),
            created_at: finding.created_at || new Date().toISOString(),
            updated_at: finding.updated_at || new Date().toISOString(),
          }));
          importedBySlide.set(slide.id, findings);
          imported += findings.length;
        }
        for (const slide of state.slides) {
          if (importedBySlide.has(slide.id)) slide.findings = importedBySlide.get(slide.id);
        }
        const slide = activeSlide();
        state.selectedFindingId = slide?.findings[0]?.id || null;
        render();
        setStatus(`Imported ${imported} finding(s) from JSON.`);
      } catch (error) {
        console.error(error);
        setStatus(`Import failed: ${error.message || "JSON could not be parsed."}`);
      }
    };
    reader.readAsText(file, "utf-8");
  }

  function beginDraw(event) {
    if (!activeSlide() || event.button !== 0) return;
    if (event.target instanceof SVGRectElement && event.target.dataset.findingId) return;
    const start = pointToNormalized(event);
    if (!start) return;
    event.preventDefault();
    elements.stage.setPointerCapture(event.pointerId);
    state.draftRect = { x: start.x, y: start.y, width: 0, height: 0 };

    const move = (moveEvent) => {
      const point = pointToNormalized(moveEvent);
      if (!point || !state.draftRect) return;
      state.draftRect.width = point.x - start.x;
      state.draftRect.height = point.y - start.y;
      renderOverlay();
    };

    const end = (upEvent) => {
      elements.stage.releasePointerCapture(upEvent.pointerId);
      elements.stage.removeEventListener("pointermove", move);
      elements.stage.removeEventListener("pointerup", end);
      elements.stage.removeEventListener("pointercancel", cancel);
      const rect = state.draftRect ? normalizeRect(state.draftRect) : null;
      state.draftRect = null;
      if (rect && rect.width > 0.005 && rect.height > 0.005) {
        addFinding(rect);
      } else {
        renderOverlay();
        setStatus("Ignored tiny rectangle drag.");
      }
    };

    const cancel = () => {
      state.draftRect = null;
      elements.stage.removeEventListener("pointermove", move);
      elements.stage.removeEventListener("pointerup", end);
      elements.stage.removeEventListener("pointercancel", cancel);
      renderOverlay();
    };

    elements.stage.addEventListener("pointermove", move);
    elements.stage.addEventListener("pointerup", end);
    elements.stage.addEventListener("pointercancel", cancel);
  }

  elements.slideFiles.addEventListener("change", (event) => loadSlides(event.target.files));
  elements.importJson.addEventListener("change", (event) => importReviewJson(event.target.files?.[0]));
  elements.exportJson.addEventListener("click", downloadJson);
  elements.form.addEventListener("submit", saveFinding);
  elements.deleteFinding.addEventListener("click", deleteSelectedFinding);
  elements.clearSlideFindings.addEventListener("click", clearSlideFindings);
  elements.fitSlide.addEventListener("click", () => { state.zoom = "fit"; applyZoom(); setStatus("Slide set to fit view."); });
  elements.actualSize.addEventListener("click", () => { state.zoom = "actual"; applyZoom(); setStatus("Slide set to actual size."); });
  elements.stage.addEventListener("pointerdown", beginDraw);
  elements.image.addEventListener("load", positionOverlay);
  window.addEventListener("resize", positionOverlay);

  render();
})();
