class LeadLogo extends HTMLElement {

  get template() {
    let t = document.createElement("template");
    t.innerHTML = `
    <style>
      a {
        text-decoration: none;
        display: flex;
      }
      img {
        display: block;
      }
    </style>
    ${this.dataset.link
      ? `<a href="${this.dataset.link}" target="_blank"><img id="lead-logo"></a>`
      : `<img id="lead-logo">`
    }`;
    return t;
  }

  /**
   * Lifecycle callbacks
   */

  constructor() {
    super();

    this.attachShadow({ mode: "open" });
    this.shadowRoot.appendChild(this.template.content.cloneNode(true));

    this.leadLogo = this.shadowRoot.querySelector("#lead-logo")
    this.leadLogo.src = this.dataset.logo;
    this.style.width = `min(${this.dataset?.maxWidth || 120}px, 100%)`;
    this.leadLogo.style.width = `min(${this.dataset?.maxWidth || 120}px, 100%)`;

    const embedInfographic = this.closest(".embed-infographic")
    if (embedInfographic) {
      embedInfographic.style.margin = 0;
    }
  }
}


// Place after the kicker
const kicker = document.querySelector('header > .kicker');
kicker && kicker.after(document.querySelector("lead-logo"));


/**
 * Register the element
 */

customElements.get("lead-logo") || customElements.define("lead-logo", LeadLogo);

/**
 * ES export
 */

export default LeadLogo;
