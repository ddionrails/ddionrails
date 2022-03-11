/** Handle referrer search url and switch email requirement status. */

const email = document.getElementById("email")

document.addEventListener("DOMContentLoaded", () => {
	const source = document.getElementById("source") as HTMLInputElement
	source.value = decodeURI(document.referrer)
})

document.getElementById("anon-submit-button").addEventListener("click",
	(event) => {
		email.removeAttribute("required")
	}

)

document.getElementById("submit-button").addEventListener("click",
	(event) => {
		email.setAttribute("required", "")
	}

)
