
/* Remove extraneous "/" from beginning, middle and end. */
function trimSlashes(str) {
  return str.replace(/^\/+|\/+$/g, '').replace(/\/+/g, '/');
}

function appendGetParams(url, params) {
  var paramString = Object.keys(params).filter(
    (param) => params[param] !== null
  ).map(
    (param) => `${param}=${encodeURIComponent(params[param])}`
  ).join("&");
  return "/api/file/?"+paramString;
}


/********* Frontend *********/

export function gallery(folder=null) {
  if(folder === null || folder.length == 0) {
    return "/gallery/folder/";
  } else {
    return "/gallery/folder/" + trimSlashes(folder);
  }
}

/* Takes a path as given in the gallery query parameter and returns a list of
 * objects describing the folders along that path. */
export function folderListFromPath(path) {
  var folders = [{
    name: "root",
    folder: "/",
    url: gallery(null),
  }];
  for(var name of trimSlashes(path).split("/")) {
    if(name == "") continue;
    var folderObj = {
      name: name,
      folder: folders[folders.length-1].folder + "/" + name,
    }
    folderObj.url = gallery(folderObj.folder);
    folders.push(folderObj);
  }
  return folders;
}


/********* Backend *********/

export function apiFileList(params) {
  //XXX Convert params to string, check there are no extras
  return appendGetParams("/api/file/", params);
}

export function apiFileDetail(fileHash) {
  return "/api/file/"+fileHash;
}

export function fileRaw(fileHash) {
  return "/file/"+fileHash+"/raw";
}

export function fileThumbnail(fileHash) {
  return "/file/"+fileHash+"/thumbnail";
}

export const fileTags = "/api/filetag/";

export const action = "/api/action";
