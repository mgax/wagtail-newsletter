window.wagtail.app.register("wn-panel",
  class extends window.StimulusModule.Controller {
    static targets = [
      "message",
      "button",
      "saveCampaign",
      "sendTestEmail",
      "sendCampaign",
      "errorMessage",
    ]

    static values = {
      loaded: Boolean,
      recipientsDescription: String,
      urls: Object,
      userEmail: String,
    }

    static classes = [
      "loading",
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

    async saveCampaign() {
      // TODO prevent concurrency

      const url = new URL('preview/', window.location.href); /* TODO set as controller value */
      const form = document.querySelector('[data-edit-form]');

      const formValue = (name) => form.querySelector(`input[name=${name}]`).value

      const savePreviewResp = await fetch(url, {
        method: 'POST',
        body: new FormData(form),
      });
      const previewState = await savePreviewResp.json();

      if (previewState.is_valid && previewState.is_available) {
        url.searchParams.set('mode', 'newsletter');
        const recipients = formValue('newsletter_recipients');
        const subject = formValue('newsletter_subject') || formValue('title');
        const previewResp = await fetch(url);
        const content = await previewResp.text();
        this.postAndReload("saveCampaign", { recipients, subject, content });
      }
      else {
        // TODO error
        console.log('failed to set preview state:', previewState);
      }
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

    loadedValueChanged(loaded) {
      this.element.classList.toggle(this.loadingClass, !loaded);
      if (!loaded) {
        this.buttonTargets.forEach(button => button.setAttribute("disabled", ""));
      }
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
