
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
