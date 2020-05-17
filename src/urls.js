export function fileDetail(fileHash) {
  return "/api/file/"+fileHash;
}

export function fileList(params={}) {
  var paramString = "";
  for(var param in params) {
    if(params[param] !== null) {
      paramString += `${param}=${encodeURIComponent(params[param])}`;
    }
  }
  return "/api/file/?"+paramString;
}
