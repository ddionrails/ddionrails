function getApiUrl(){

  const variableMeta = document.querySelector('meta[name="variable"]');
  const variableName = variableMeta instanceof HTMLMetaElement
    ? variableMeta.content
    : "";
  const datasetMeta = document.querySelector('meta[name="dataset"]');
  const datasetName = datasetMeta instanceof HTMLMetaElement
    ? datasetMeta.content
    : "";

  if ( variableName == "" || datasetName == ""){
    return "";
  }

  return `${window.location.origin}/api/related_variables/?dataset=${datasetName}&variable=${variableName}`


}

function loadRelationData(){
  const apiUrl = getApiUrl()
  if (apiUrl == ""){
    return;
  }

  let apiRequest = new Request(apiUrl)
  fetch(apiRequest).then(
    (response) => {
      response.json().then(
        (json)=>{
      console.log(json);
      })
    }
  )



}

window.addEventListener("load", ()=>{
  loadRelationData()

})
