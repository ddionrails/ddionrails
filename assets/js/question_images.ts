const images = JSON.parse(
	document.getElementById("question-images").textContent
);
const questionImagesContainer = document.getElementById("question-images-container")

const imageButton = document.createElement("button")
imageButton.type = "button"
imageButton.classList.add("btn")
imageButton.classList.add("btn-link")
imageButton.setAttribute("data-toggle", "modal")

for (const language of ["de", "en"]) {
	if (Object.keys(images).length === 0) {
		continue
	}
	const label = images[language]["label"]
	if (label === "") {
		continue
	}
	const button: HTMLElement = imageButton.cloneNode(true) as HTMLElement
	button.setAttribute("data-target", `#image-${language}-modal`)
	button.textContent = `${label}: ${language}`
	questionImagesContainer.appendChild(button)

	const modalContainer = document.getElementById(`image-${language}-modal-content`)
	const image = document.createElement("img")
	image.setAttribute("src", images[language]["url"])
	modalContainer.appendChild(image)
}

