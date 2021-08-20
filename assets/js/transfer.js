
const FIRST_FRAME = document.getElementById("main-frame");
const SECOND_FRAME = document.getElementById("second-frame");


/**
 *  Resize given iframe so it does not display a scrollbar.
 *
 * @param {*} iFrame An iframe DOM Element Object
 */
function resizeIFrameToFitContent( iFrame ) {
  iFrame.width = iFrame.contentWindow.document.body.scrollWidth;
  iFrame.height = iFrame.contentWindow.document.body.scrollHeight;
}

/**
 *
 * @param {*} observedElement shiny range slider DOM element to observe
 * @param {*} inputToUpdate shiny text input to update with slider element value
 */
function setYearRangeObserver(observedElement, inputToUpdate) {
  const rangeEndPointObserver = new WebKitMutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      inputToUpdate.value = mutation.target.textContent;
      inputToUpdate.dispatchEvent(new KeyboardEvent("keyup", {"key": 13}));
    });
  });
  rangeEndPointObserver.observe(observedElement, {childList: true});
}


/**
 * Wait for a shiny app iframe to fully load its plot.
 *
 * Is used to resize iframe according to plot size.
 *
 * @param {*} iFrame An iframe DOM Element Object
 * @param {*} init Flag to denote second frames initialization
 */
async function waitForIFrameContent(iFrame, init=false) {
  while ( iFrame.contentDocument.getElementsByClassName("plot-container").length === 0) {
    await new Promise((r) => setTimeout(r, 100));
  }
  if (init) {
    startYear = iFrame.contentDocument.getElementById("start_year");
    endYear = iFrame.contentDocument.getElementById("end_year");

    startYear.classList.add("hidden");
    endYear.classList.add("hidden");

    const firstFrameContent = FIRST_FRAME.contentDocument;

    sliderStartYear = firstFrameContent.getElementsByClassName("irs-from")[0];
    sliderEndYear = firstFrameContent.getElementsByClassName("irs-to")[0];

    setYearRangeObserver(sliderStartYear, startYear.querySelector("input"));
    setYearRangeObserver(sliderEndYear, endYear.querySelector("input"));
  }
  resizeIFrameToFitContent( iFrame );
}


const documentURL = new URL(document.URL);
const documentVariable = documentURL.searchParams.get("variable");
const serverMetadata = JSON.parse(
  document.getElementById("transfer-server-metadata").textContent
);

/**
 * Add handlers to manage UI elements to display/hide secondary plot.
 */
window.addEventListener("load", function() {
  const addButton = document.getElementById("second-plot-button");
  const closeIcon = document.getElementById("close-icon");

  addButton.addEventListener("click", function() {
    if ( SECOND_FRAME.getAttribute("src") === "") {
      const firstFrameContent = FIRST_FRAME.contentDocument;
      sliderStartYearText = firstFrameContent.getElementsByClassName(
        "irs-from")[0].textContent;
      sliderEndYearText = firstFrameContent.getElementsByClassName(
        "irs-to")[0].textContent;
      frameURL = new URL(serverMetadata["url"]);
      frameURL.searchParams.append("variable", documentVariable);
      frameURL.searchParams.append("no-title", "TRUE");
      frameURL.searchParams.append("start-year", sliderStartYearText);
      frameURL.searchParams.append("end-year", sliderEndYearText);
      SECOND_FRAME.src = frameURL;

      waitForIFrameContent(SECOND_FRAME, init=true);
    }
    SECOND_FRAME.classList.remove("hidden");
    closeIcon.classList.remove("hidden");
    addButton.classList.add("hidden");
    waitForIFrameContent(SECOND_FRAME);
  });

  closeIcon.addEventListener("click", function() {
    console.log("test");
    SECOND_FRAME.classList.add("hidden");
    closeIcon.classList.add("hidden");
    addButton.classList.remove("hidden");
  } );
});


document.addEventListener("load", waitForIFrameContent(FIRST_FRAME));
