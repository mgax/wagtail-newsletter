window.wagtail.app.register("wn-panel",
  class extends window.StimulusModule.Controller {
    static targets = [
      "message",
      "button",
      "saveDraft",
      "sendTestEmail",
      "sendCampaign",
    ]

    static values = {
      loaded: Boolean,
      urls: Object,
      userEmail: String,
    }

    static classes = [
      "loading",
    ]

    initialize() {
      if (!this.loadedValue) {
        this.getCampaign();
      }
    }

    getCampaign() {
      this.postAndReload("getCampaign");
    }

    saveDraft() {
      this.postAndReload("saveDraft");
    }

    sendTestEmail() {
      const email = prompt("Send test email to:", this.userEmailValue);
      if (email === null) return;
      this.postAndReload("sendTestEmail", { email });
    }

    sendCampaign() {
      this.postAndReload("sendCampaign");
    }

    loadedValueChanged(loaded) {
      this.element.classList.toggle(this.loadingClass, !loaded);
      if (!loaded) {
        this.buttonTargets.forEach(button => button.setAttribute("disabled", ""));
      }
    }

    async post(url, body) {
      const csrfInput = document.querySelector("input[name=csrfmiddlewaretoken]");
      const resp = await fetch(
        url,
        {
          method: "POST",
          mode: "same-origin",
          headers: {
            "X-CSRFToken": csrfInput.value,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
        }
      );
      return await resp.text();
    }

    async postAndReload(urlName, body) {
      this.loadedValue = false;
      const html = await this.post(this.urlsValue[urlName], body);
      const div = document.createElement("div");
      div.innerHTML = html;
      this.element.replaceWith(div.querySelector(".wn-panel"));
    }
  }
);
