/* Actions
 * A tool to change state on both backend and frontend. This JS class modifies
 * state on the frontend immediately, then gets serialized and sent to the
 * backend to change the same state there.
 */

export function deserialize(data) {
  let typeClass = {
  }[data.type];
  return typeClass.deserialize(data.data);
}

class Action {
  static stateNeeded = null;

  serialize() {
    return {
      type: this.constructor.name,
      data: this._serialize(),
    };
  }

  _serialize() { }

  static _deserialize(data) { }

  do(stateVars) { }
}


export class TagUpdate extends Action {
  static stateNeeded = ["tags"];

  constructor(tags) {
    super()
    this.tags = tags;
  }

  _serialize() {
    return {tags: this.tags};
  }

  static _deserialize(data) {
    return new constructor(data.tags);
  }

  do() {
    return {
      tags: this.tags,
    };
  }
}

export class FileTagUpdate extends Action {
  static stateNeeded = ["files"];

  constructor(fileTagsToAdd, fileTagsToRemove) {
    super()
    this.fileTagsToAdd = fileTagsToAdd;
    this.fileTagsToRemove = fileTagsToRemove;
  }

  _serialize() {
    return {
      fileTagsToAdd: this.fileTagsToAdd,
      fileTagsToRemove: this.fileTagsToRemove,
    };
  }

  static _deserialize(data) {
    return new constructor(data.fileTagsToAdd, data.fileTagsToRemove);
  }

  do({files}) {
    for(let fileTag of this.fileTagsToAdd) {
      this._do_add_or_remove(files, fileTag.file, fileTag.tag, true);
    }
    for(let fileTag of this.fileTagsToRemove) {
      this._do_add_or_remove(files, fileTag.file, fileTag.tag, false);
    }
    return { files }
  }

  _do_add_or_remove(files, hash, tag, add) {
    let fileInfo = files.find(f => f.hash === hash);
    if(fileInfo === undefined) {
      return;
    }

    if(add) {
      fileInfo.tags.push(tag);
    } else {
      let idx = fileInfo.tags.indexOf(tag);
      if(idx !== -1) {
      fileInfo.tags.splice(idx, 1);
      }
    }
  }

}
