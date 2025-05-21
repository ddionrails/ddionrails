export function VariableNames({ language }: { language: string }) {
  return <SearchBox language={language} />;
}

function SearchBox({ language }: { language: string }) {
  return (
    <div className="sui-layout-header">
      <div className="sui-search-box">
        <input
          className="sui-search-box__text-input"
          id="downshift-2-input"
          placeholder={language == "en" ? "Search" : "Suche"}
	  onKeyDown={searchWithEnter}
        ></input>
        <input
          data-transaction-name="search submit"
          type="submit"
          className="button sui-search-box__submit"
          value="Search"
	  onClick={search}
        />
      </div>
    </div>
  );
}

function searchWithEnter(event: React.KeyboardEvent<HTMLInputElement>){
	if(event.key === "Enter"){
		search()
	}
}


function search() {
  const inputElement = document.getElementById("downshift-2-input") as HTMLInputElement;
  const inputText = inputElement.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  if (inputText.trim() === ""){
	  return
  }
  fetch("/elastic/variables/_search", {
    method: "POST",
    body: JSON.stringify({
      query: {
        regexp: {
          name: {
            value: ".*" + inputText,
            flags: "ALL",
            case_insensitive: true,
            max_determinized_states: 10000,
          },
        },
      },
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8",
    },
  });
}
