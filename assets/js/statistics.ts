
const FIRST_FRAME = document.getElementById("main-frame") as HTMLIFrameElement;
const SECOND_FRAME = document.getElementById("second-frame") as HTMLIFrameElement;
const VARIABLE_METADATA = JSON.parse(document.getElementById("variable-metadata").textContent)
const STATISTIC_SERVER_METADATA = JSON.parse(document.getElementById("statistics-server-metadata").textContent)
let loadingSpinner = document.getElementById("loading-spinner");
const infoIcon = document.createElement("i");
infoIcon.classList.add("fas");
infoIcon.classList.add("fa-info-circle");
// This could be done through ingesting a style link into the iframe.
// But this solution seems more clear since it is more centralized.
infoIcon.style.cssText = `
  cursor: pointer;
  color: #007bff;
  font-size: 0.85em
`;

function setFirstFrameUrl() {
  const firstFrameURL = new URL(STATISTIC_SERVER_METADATA["url"]);
  firstFrameURL.searchParams.append("variable", VARIABLE_METADATA["variable"])
  firstFrameURL.searchParams.append("no-title", "TRUE")
  appendYLimitQueryParams(firstFrameURL)
  FIRST_FRAME.src = String(firstFrameURL)
}


/**
 * Add y-scale-limit query params to URL.
 * 
 * @param url URL to add query params to
 */
function appendYLimitQueryParams(url: URL) {
  if ("y_limits" in VARIABLE_METADATA) {
    url.searchParams.append("y-min", VARIABLE_METADATA["y_limits"]["min"])
    url.searchParams.append("y-max", VARIABLE_METADATA["y_limits"]["max"])
  }
}



/**
 *  Resize given iframe so it does not display a scrollbar.
 *
 * @param {*} iFrame An iframe DOM Element Object
 */
function resizeIFrameToFitContent(iFrame: HTMLIFrameElement) {
  iFrame.width = String(iFrame.contentWindow.document.body.scrollWidth);
  iFrame.height = String(iFrame.contentWindow.document.body.scrollHeight);
}

/**
 *
 * @param {*} observedElement shiny range slider DOM element to observe
 * @param {*} inputToUpdate shiny text input to update with slider element value
 */
function initYearRangeObserver(observedElement: HTMLElement, inputToUpdate: HTMLInputElement) {
  const rangeEndPointObserver = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      inputToUpdate.value = mutation.target.textContent;
      inputToUpdate.dispatchEvent(new KeyboardEvent("keyup", {"key": "13"}));
    });
  });
  rangeEndPointObserver.observe(observedElement, {childList: true});
}

/**
 * Get year range slider of main plot and set up the second plots value fields.
 *
 * The year range slider of the main plot iframe is observe to
 * set the range of a second plot iframe according to the first.
 *
 * @param {*} iFrame The frame with the year fields to be
 *                   linked to the year range slider of the main iFrame.
 */
function setupYearRangeObserver(iFrame: HTMLIFrameElement) {
  const startYear = iFrame.contentDocument.getElementById("start_year");
  const endYear = iFrame.contentDocument.getElementById("end_year");

  startYear.classList.add("hidden");
  endYear.classList.add("hidden");

  const firstFrameContent = FIRST_FRAME.contentDocument;

  const sliderStartYear: HTMLElement = firstFrameContent.querySelector(".irs-from");
  const sliderEndYear: HTMLElement = firstFrameContent.querySelector(".irs-to");

  initYearRangeObserver(sliderStartYear, startYear.querySelector("input"));
  initYearRangeObserver(sliderEndYear, endYear.querySelector("input"));
}

/**
 * Add icon to an iFrame that acts as stand in for a modal button in the main window.
 * @param {*} iFrame
 */
function setupConfidenceIntervalModal(iFrame: HTMLIFrameElement) {
  const container = iFrame.contentDocument.getElementById("confidence_interval")
    .parentNode.parentNode;
  const button = infoIcon.cloneNode();
  button.addEventListener("click", function () {
    document.getElementById("ci-button").click();
  });
  container.appendChild(button); // infoButton.cloneNode(deep=true));
}

/**
 * Wait for a shiny app iframe to fully load its plot.
 *
 * Is used to resize iframe according to plot size.
 *
 * @param {*} iFrame An iframe DOM Element Object
 * @param {*} init Flag to denote second frames initialization
 */
async function waitForIFrameContent(iFrame: HTMLIFrameElement, init: boolean = false) {
  while (iFrame.contentDocument.getElementsByClassName("plot-container").length === 0) {
    await new Promise((r) => setTimeout(r, 100));
  }
  if (init) {
    setupYearRangeObserver(iFrame);
    setupConfidenceIntervalModal(SECOND_FRAME);
  }
  resizeIFrameToFitContent(iFrame);
  if (loadingSpinner != null) {
    setupConfidenceIntervalModal(FIRST_FRAME);
    loadingSpinner.remove();
    loadingSpinner = null;
  }
}



/**
 * Add handlers to manage UI elements to display/hide secondary plot.
 */
window.addEventListener("load", function () {
  const addButton = document.getElementById("second-plot-button");
  const closeIcon = document.getElementById("close-icon");

  addButton.addEventListener("click", function () {
    if (SECOND_FRAME.getAttribute("src") === "") {
      const firstFrameContent = FIRST_FRAME.contentDocument;
      const sliderStartYearText = firstFrameContent.querySelector(
        ".irs-from").textContent;
      const sliderEndYearText = firstFrameContent.querySelector(
        ".irs-to").textContent;
      const frameURL = new URL(STATISTIC_SERVER_METADATA["url"]);
      frameURL.searchParams.append("variable", VARIABLE_METADATA["variable"]);
      frameURL.searchParams.append("no-title", "TRUE");
      frameURL.searchParams.append("start-year", sliderStartYearText);
      frameURL.searchParams.append("end-year", sliderEndYearText);
      appendYLimitQueryParams(frameURL)

      SECOND_FRAME.src = String(frameURL);

      waitForIFrameContent(SECOND_FRAME, true);
    }
    SECOND_FRAME.classList.remove("hidden");
    closeIcon.classList.remove("hidden");
    addButton.classList.add("hidden");
    waitForIFrameContent(SECOND_FRAME);
  });

  closeIcon.addEventListener("click", function () {
    console.log("test");
    SECOND_FRAME.classList.add("hidden");
    closeIcon.classList.add("hidden");
    addButton.classList.remove("hidden");
  });

  waitForIFrameContent(FIRST_FRAME)
});

document.getElementById("statistics-nav-item").classList.add("nav-item-active");
setFirstFrameUrl();

