window.wagtail.app.register("wn-panel",
  class extends window.StimulusModule.Controller {
    static targets = [
      "message",
      "button",
      "saveDraft",
      "sendTestEmail",
      "sendCampaign",
      "errorMessage",
    ]

    static values = {
      loaded: Boolean,
      recipientsDescription: String,
      unsaved: Boolean,
      urls: Object,
      userEmail: String,
    }

    static classes = [
      "loading",
      "unsaved",
      "error",
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
      const answer = confirm(`Send campaign to ${this.recipientsDescriptionValue}?`);
      if (answer) {
        this.postAndReload("sendCampaign");
      }
    }

    unsaved() {
      this.unsavedValue = true;
    }

    loadedValueChanged(loaded) {
      this.element.classList.toggle(this.loadingClass, !loaded);
      if (!loaded) {
        this.buttonTargets.forEach(button => button.setAttribute("disabled", ""));
      }
    }

    unsavedValueChanged(unsaved) {
      this.element.classList.toggle(this.unsavedClass, unsaved);
    }

    async post(url, body) {
      this.messageTarget.textContent = "...";
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
      if (resp.status < 200 || resp.status >= 300) {
        throw new Error("Request failed");
      }
      return await resp.text();
    }

    async postAndReload(urlName, body) {
      this.loadedValue = false;
      try {
        const html = await this.post(this.urlsValue[urlName], body);
        const div = document.createElement("div");
        div.innerHTML = html;
        this.element.replaceWith(div.querySelector(".wn-panel"));
      }
      catch (e) {
        this.loadedValue = true;
        this.element.classList.add(this.errorClass);
        this.errorMessageTarget.textContent = "Action failed";
        console.error(e);
      }
    }
  }
);
