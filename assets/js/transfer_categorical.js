const documentURL = new URL(document.URL);
const documentVariable = documentURL.searchParams.get("variable");
const serverMetadata = JSON.parse(
  document.getElementById("transfer-server-metadata").textContent
);


window.addEventListener("load", function() {
  const addButton = document.getElementById("secondary-plot");
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
  });

  closeIcon.addEventListener("click", function() {
    console.log("test");
    secondIframe = document.getElementById("second-frame");
    secondIframe.classList.add("hidden");
    closeIcon.classList.add("hidden");
    addButton.classList.remove("hidden");
  } );
});
