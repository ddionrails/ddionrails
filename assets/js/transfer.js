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
 * Wait for a shiny app iframe to fully load its plot.
 *
 * Is used to resize iframe according to plot size.
 *
 * @param {*} iFrame An iframe DOM Element Object
 */
async function waitForIFrameContent(iFrame) {
  console.log("calling");
  while ( iFrame.contentDocument.getElementsByClassName("plot-container").length === 0) {
    await new Promise((r) => setTimeout(r, 100));
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
  const firstFrame = document.getElementById("main-frame");

  addButton.addEventListener("click", function() {
    secondIframe = document.getElementById("second-frame");
    if ( secondIframe.getAttribute("src") === "") {
      fromYear = firstFrame.contentDocument.getElementsByClassName(
        "irs-from")[0].textContent;
      toYear = firstFrame.contentDocument.getElementsByClassName(
        "irs-to")[0].textContent;
      frameURL = new URL(serverMetadata["url"]);
      frameURL.searchParams.append("variable", documentVariable);
      frameURL.searchParams.append("no-title", "TRUE");
      frameURL.searchParams.append("from", fromYear);
      frameURL.searchParams.append("to", toYear);
      secondIframe.src = frameURL;
    }
    secondIframe.classList.remove("hidden");
    closeIcon.classList.remove("hidden");
    addButton.classList.add("hidden");
    waitForIFrameContent(secondIframe);
  });

  closeIcon.addEventListener("click", function() {
    console.log("test");
    secondIframe = document.getElementById("second-frame");
    secondIframe.classList.add("hidden");
    closeIcon.classList.add("hidden");
    addButton.classList.remove("hidden");
  } );
});

const mainFrame = document.getElementById("main-frame");

document.addEventListener("load", waitForIFrameContent(mainFrame));
