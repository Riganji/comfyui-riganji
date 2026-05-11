import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ImageResizer.SizeDisplay",

    nodeCreated(node) {
        if (node.comfyClass !== "ImageResizer") return;

        // ── helpers ──────────────────────────────────────────────────────────

        function getWidget(name) {
            return node.widgets?.find(w => w.name === name);
        }

        /** Try to read pixel dimensions from whatever is connected to the image input. */
        function getSourceSize() {
            const imageInput = node.inputs?.find(i => i.name === "image");
            if (!imageInput?.link) return null;

            const link   = app.graph.links[imageInput.link];
            if (!link) return null;

            const srcNode = app.graph.getNodeById(link.origin_id);
            if (!srcNode) return null;

            // LoadImage stores size after execution
            if (srcNode.imageSize) return srcNode.imageSize;               // [w, h]
            if (srcNode.imgs?.[0]) {
                const img = srcNode.imgs[0];
                return [img.naturalWidth, img.naturalHeight];
            }
            return null;
        }

        function computeOutput(srcW, srcH) {
            const method  = getWidget("resize_method")?.value  ?? "Scale Factor";
            const factor  = getWidget("scale_factor")?.value   ?? 2.0;
            const setW    = getWidget("set_width")?.value      ?? 0;
            const setH    = getWidget("set_height")?.value     ?? 0;

            if (method === "Scale Factor") {
                if (!srcW) return { label: `× ${factor}`, known: false };
                return {
                    w: Math.round(srcW * factor),
                    h: Math.round(srcH * factor),
                    known: true
                };
            } else {
                // Set Size
                if (setW === 0 && setH === 0) {
                    return srcW
                        ? { w: srcW, h: srcH, known: true }
                        : { label: "no change", known: false };
                }
                if (setW === 0) {
                    if (!srcW) return { label: `auto × ${setH}`, known: false };
                    return { w: Math.round(srcW * (setH / srcH)), h: setH, known: true };
                }
                if (setH === 0) {
                    if (!srcW) return { label: `${setW} × auto`, known: false };
                    return { w: setW, h: Math.round(srcH * (setW / srcW)), known: true };
                }
                return { w: setW, h: setH, known: true };
            }
        }

        // ── display widget ───────────────────────────────────────────────────

        const display = node.addWidget("text", "size_info", "", () => {}, {
            serialize: false,
        });
        display.disabled   = true;
        display.computeSize = () => [node.size[0], 26];

        // Override draw so we can style the text ourselves
        display.draw = function(ctx, node, widgetWidth, y, H) {
            ctx.save();
            ctx.font         = "bold 13px monospace";
            ctx.textAlign    = "center";
            ctx.textBaseline = "middle";
            ctx.fillStyle    = "rgba(255,255,255,0.75)";
            ctx.fillText(this.value, widgetWidth / 2, y + H / 2);
            ctx.restore();
        };

        // ── update function ──────────────────────────────────────────────────

        function updateVisibility() {
            const method     = getWidget("resize_method")?.value ?? "Scale Factor";
            const isScale    = method === "Scale Factor";

            const scaleFactor = getWidget("scale_factor");
            const setWidth    = getWidget("set_width");
            const setHeight   = getWidget("set_height");

            if (scaleFactor) scaleFactor.disabled = !isScale;
            if (setWidth)    setWidth.disabled    = isScale;
            if (setHeight)   setHeight.disabled   = isScale;
        }

        function update() {
            updateVisibility();

            const src    = getSourceSize();
            const result = computeOutput(src?.[0], src?.[1]);

            if (result.known) {
                const srcPart = src ? `${src[0]} × ${src[1]}  →  ` : "";
                display.value = `${srcPart}${result.w} × ${result.h}`;
            } else {
                display.value = result.label;
            }

            app.graph.setDirtyCanvas(true, false);
        }

        // ── hook into every widget's callback ────────────────────────────────

        // We need to wrap callbacks *after* all widgets are added.
        // Use a short timeout to ensure widgets are fully initialised.
        setTimeout(() => {
            for (const w of node.widgets ?? []) {
                if (w === display) continue;
                const orig = w.callback;
                w.callback = function(...args) {
                    orig?.apply(this, args);
                    update();
                };
            }
            update();
        }, 0);

        // Also re-evaluate when connections change
        const origOnConnectionsChange = node.onConnectionsChange;
        node.onConnectionsChange = function(...args) {
            origOnConnectionsChange?.apply(this, args);
            update();
        };
    },
});
