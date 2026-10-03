import {
  askCvAssistant,
  initializeCvChat
} from "./cv-chat-engine.js";

const GPU_REQUIREMENT_MESSAGE =
  "This CV assistant runs on your device and needs a capable GPU. Your device may not meet that requirement—please try again on a device with a supported GPU.";

const GPU_CAPACITY_ERROR_MESSAGE =
  "The CV assistant could not run reliably on this device’s GPU. Please try again on a device with a more capable GPU.";

const MIN_SYSTEM_MEMORY_GB = 8;
const MIN_MAX_BUFFER_SIZE = 1024 * 1024 * 1024;
const MIN_STORAGE_BUFFER_BINDING_SIZE = 128 * 1024 * 1024;

document.addEventListener("DOMContentLoaded", () => {
  const openButtons = [
    document.getElementById("cv-chat-open"),
    document.getElementById("cv-chat-floating")
  ].filter(Boolean);

  const windowBox = document.getElementById("cv-chat-window");
  const closeButton = document.getElementById("cv-chat-close");
  const form = document.getElementById("cv-chat-form");
  const input = document.getElementById("cv-chat-input");
  const messages = document.getElementById("cv-chat-messages");
  const status = document.getElementById("cv-chat-status");

  if (!windowBox || !form || !input || !messages || !status) return;

  let deviceCheckPromise = null;
  let deviceSupported = false;
  let requirementMessageShown = false;

  function addMessage(text, type) {
    const message = document.createElement("div");
    message.className = `cv-chat-message ${type}`;
    message.textContent = text;
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
    return message;
  }

  function setFormEnabled(enabled) {
    for (const control of form.querySelectorAll("input, button, textarea")) {
      control.disabled = !enabled;
    }
  }

  function showGpuRequirement(message = GPU_REQUIREMENT_MESSAGE) {
    if (!requirementMessageShown) {
      addMessage(message, "ai");
      requirementMessageShown = true;
    }

    status.textContent = "GPU requirements not met";
    setFormEnabled(false);
  }

  async function assessDeviceCapacity() {
    if (
      !navigator.gpu ||
      typeof navigator.gpu.requestAdapter !== "function"
    ) {
      return {
        supported: false,
        reason: "WebGPU is not available in this browser."
      };
    }

    const adapter = await navigator.gpu.requestAdapter({
      powerPreference: "high-performance"
    });

    if (!adapter) {
      return {
        supported: false,
        reason: "No compatible GPU adapter found."
      };
    }

    const adapterInfo = adapter.info || {};

    if (adapterInfo.isFallbackAdapter === true) {
      return {
        supported: false,
        reason: "Only a software fallback adapter is available."
      };
    }

    const memoryGb = Number(navigator.deviceMemory);

    if (Number.isFinite(memoryGb) && memoryGb < MIN_SYSTEM_MEMORY_GB) {
      return {
        supported: false,
        reason: "The device has limited system memory for local model inference."
      };
    }

    const limits = adapter.limits || {};
    const maxBufferSize = Number(limits.maxBufferSize);
    const maxStorageBufferBindingSize = Number(
      limits.maxStorageBufferBindingSize
    );

    if (
      !Number.isFinite(maxBufferSize) ||
      maxBufferSize < MIN_MAX_BUFFER_SIZE ||
      !Number.isFinite(maxStorageBufferBindingSize) ||
      maxStorageBufferBindingSize < MIN_STORAGE_BUFFER_BINDING_SIZE
    ) {
      return {
        supported: false,
        reason: "The GPU does not report enough WebGPU buffer capacity for this model."
      };
    }

    return { supported: true, reason: null };
  }

  function ensureDeviceSupport() {
    if (!deviceCheckPromise) {
      status.textContent = "Checking device compatibility…";
      setFormEnabled(false);

      deviceCheckPromise = assessDeviceCapacity()
        .then((result) => {
          deviceSupported = result.supported;

          if (deviceSupported) {
            status.textContent = "Ready";
            setFormEnabled(true);
          } else {
            console.info("CV assistant unavailable:", result.reason);
            showGpuRequirement();
          }

          return deviceSupported;
        })
        .catch((error) => {
          console.warn("CV assistant device check failed:", error);
          deviceSupported = false;
          showGpuRequirement();
          return false;
        });
    }

    return deviceCheckPromise;
  }

  function openChat() {
    windowBox.classList.add("active");
    windowBox.setAttribute("aria-hidden", "false");
    void ensureDeviceSupport();
  }

  for (const button of openButtons) {
    button.addEventListener("click", openChat);
  }

  if (closeButton) {
    closeButton.addEventListener("click", () => {
      windowBox.classList.remove("active");
      windowBox.setAttribute("aria-hidden", "true");
    });
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!(await ensureDeviceSupport())) return;

    const question = input.value.trim();
    if (!question) return;

    addMessage(question, "user");
    input.value = "";

    const loading = addMessage("Loading local AI…", "ai");
    setFormEnabled(false);

    try {
      status.textContent = "Initializing local AI model…";

      await initializeCvChat((progress) => {
        if (progress.message) {
          status.textContent = progress.message;
        }
      });

      status.textContent = "Searching CV knowledge…";

      const result = await askCvAssistant(question, {
        onProgress: (progress) => {
          if (progress.message) {
            status.textContent = progress.message;
          }
        }
      });

      loading.remove();
      addMessage(result.answer, "ai");
      status.textContent = "Ready";
      setFormEnabled(true);
    } catch (error) {
      console.error("CV assistant error:", error);
      loading.remove();

      const errorText = String(error?.message || error);

      if (
        /out of memory|allocation failed|failed to allocate|device lost|insufficient.*memory|gpu.*memory/i.test(
          errorText
        )
      ) {
        deviceSupported = false;
        showGpuRequirement(GPU_CAPACITY_ERROR_MESSAGE);
      } else {
        addMessage(
          "The CV assistant could not start. Please try again later.",
          "ai"
        );
        status.textContent = "Unable to start";
        setFormEnabled(true);
      }
    }
  });
});
