window.wagtail.app.register("wn-send",
  class extends window.StimulusModule.Controller {
    static targets = [
      "saveDraft",
      "sendTestEmail",
      "sendCampaign",
      "testEmailRecipient",
    ]

    static values = {
      recipientsDescription: String,
      userEmail: String,
    }

    initialize() {
      this.sendTestEmailTarget.addEventListener("click", (event) => {
        const email = prompt("Send test email to:", this.userEmailValue);
        if (email === null) {
          event.preventDefault();
          return;
        }
        this.testEmailRecipientTarget.value = email;
      });

      this.sendCampaignTarget.addEventListener("click", (event) => {
        if (this.recipientsDescriptionValue) {
          const answer = confirm(`Send campaign to ${this.recipientsDescriptionValue}?`);
          if (! answer) {
            event.preventDefault();
          }
        }
        else {
          event.preventDefault();
          alert("Please select recipients before sending the campaign.");
        }
      });
    }
  }
);
