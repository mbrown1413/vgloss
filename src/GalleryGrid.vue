<template>
  <div class="gallery-grid" @mousedown="onMouseDown">
    <div class="gallery-items">
      <div
        v-for="item in items"
        :key="item.name"
        :ref="'item:'+item.name"
        class="gallery-item-container"
      >
        <div
          class="gallery-item"
          :class="{'gallery-item-selected': selectedItemSet.has(item.name)}"
          @dblclick="$emit('doubleClick', item.name)"
        >
          <div
            class="gallery-item-image"
            :style="{backgroundImage: 'url(/file/'+item.hash+'/thumbnail)'}"
          />
          {{ item.name }}
        </div>
      </div>
    </div>
    <div
      class="gallery-select-overlay"
      :style="selectOverlayStyle"
    />
  </div>
</template>

<style>
  /* Grid Item Layout */
  .gallery-grid {
    /* Hide x overflow because the select overlay may "overflow" into the
     * y-scrollbar. We wouldn't want an x-scrollbar to display when this
     * happens. */
    overflow-x: hidden;
    /* Force a scrollbar on y even if not needed, so if items change and we
     * need scroll, we don't make the jarring change of adding a scrollbar. */
    overflow-y: scroll;
    /* Non-static position forces the select overlay to be positioned relative
     * to this. */
    position: relative;
    /* Ensures user can click in blank area below any items to drag or clear
     * selection */
    height: 100%;
  }
  .gallery-items {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    grid-gap: 0.5rem;
    align-items: center;
    padding: 0.5em;
    user-select: none;
    overflow-wrap: break-word;
  }
  .gallery-item {
    border: 1px solid #d0d0d0;
    border-radius: 5%;
    cursor: pointer;
  }
  .gallery-item:hover {
    border: 1px solid black;
  }
  .gallery-item-image {
    border-radius: 5% 5% 0 0;
    background-position: center center;
    background-size: contain;
    background-repeat: no-repeat;
    /* Padding trick to fix aspect ratio:
     * https://css-tricks.com/aspect-ratio-boxes/
     */
    width: 100%;
    padding-bottom: 100%;
  }

  /* Item Selection */
  .gallery-select-overlay {
    position: absolute;
    z-index: 99;
    background-color: rgba(0, 0, 0, 0.25);
    border: solid 1px black;
  }
  .gallery-item-selected {
    border: solid 1px black;
    background-color: rgba(0, 0, 0, 0.25);
  }
</style>

<script>

/* Coordinate Systems
 *
 * Page coordinates:
 *   Origin is the top left of the page, independent of where the browser is
 *   currently scrolled.
 * Client Coordinates:
 *   Origin is at the top left of the window, dependent on where the browser is
 *   currently scrolled.
 * Element coordinates:
 *   Relative to the top left of the gallery element, not affected by the
 *   gallery element itself scrolling.
 *
 * Page and client coordinates are defined here:
 *   https://javascript.info/coordinates
 *
 *            Page
 * +........................+
 * .Page     Element        .
 * .coords ............     .
 * .       .Element   .     .
 * .       .coords    .     .
 * +---------------------+  .
 * |Client .          .  |  .
 * |coords .          .  |  .
 * |       +----------+  |  .
 * |       |Gallery   |  |  .
 * |       |Element   |  |  .
 * |       +----------+  |  .
 * |       .          .  |  .
 * |       .          .  |  .
 * |       ............  |  .
 *
 */

/* Clip a rectangle by a bounding rectangle */
function boundRect(rect, boundingRect) {
  return {
    left:   Math.max(rect.left,   boundingRect.left),
    right:  Math.min(rect.right,  boundingRect.right),
    top:    Math.max(rect.top,    boundingRect.top),
    bottom: Math.min(rect.bottom, boundingRect.bottom),
  };
}

/* Return true if the two rectangles intersect. */
function rectIntersect(rect1, rect2) {
  return !(
    // One rect is to above/below other
    rect1.top >= rect2.bottom || rect2.top >= rect1.bottom ||
    // One rect is to left/right of other
    rect1.left >= rect2.right || rect2.left >= rect1.right
  )
}

/* Return true if the point is inside the rectangle. */
function pointInRect(point, rect) {
  return point.x >= rect.left && point.x <= rect.right &&
         point.y >= rect.top && point.y <= rect.bottom;
}


/* GalleryGrid
 * Displays a grid of items with names and icon images.
 *
 * Items are passed in with the "items" prop, which is a list of objects with
 * "name" and "image" properties. "name" must be unique, as it is used to
 * identify the item for selection and event purposes.
 *
 * Zero or more items can be selected at a time. The user interaction for
 * selecting items is modeled after thunar:
 *   * Click or drag to select
 *   * Click or drag with ctrl held down to toggle selection of items.
 *   * Click with shift held down to select only items between the last
 *     selected item and the clicked item.
 * TODO: Not yet implemented:
 *   * Keyboard support
 *   * aria-selected for accessibility
 *       See: https://www.stefanjudis.com/blog/aria-selected-and-when-to-use-it/
 */
export default {
  name: 'GalleryGrid',
  props: {
    items: {
      type: Array,
      required: true,
    },
    selectedItems: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  model: {
    prop: "selectedItems",
    event: "change",
  },

  data() {
    return {
      mouseDown: false,
      lastSelectedItem: null,
      selectedItemCounter: 1,
      // Start and end points of drag selection, in element coordinates.
      selectStart: null,
      selectEnd: null,
    };
  },

  created() {
    this._selectedItemSet = new Set(this.selectedItems);
  },

  computed: {
    /* Rectangle of selection box in element coordinates. */
    selectRect() {
      if(this.mouseDown && this.selectStart && this.selectEnd) {
        return {
          left:   Math.min(this.selectStart.x, this.selectEnd.x),
          right:  Math.max(this.selectStart.x, this.selectEnd.x),
          top:    Math.min(this.selectStart.y, this.selectEnd.y),
          bottom: Math.max(this.selectStart.y, this.selectEnd.y),
        };
      } else {
        return null;
      }
    },

    /* Since Vue can't react to Set changes, we do a bit of a hack here. The
     * counter selectedItemCounter will increment whenever we add/remove items.
     * selectedItemSet contains the actual set, while the computed property
     * selectedItems can be used as normal. Of course, you have to increment
     * the counter whenever selectedItemSet changes. Using selectionAdd,
     * selectionDelete, selectionToggle, etc. will handle this seamlessly.
     * TODO: Support for watching Sets is planned for Vue 3!
     *        https://github.com/vuejs/vue/issues/2410
     */
    selectedItemSet() {
      if(this.selectedItemCounter > 0) {  // Always True
        return this._selectedItemSet || new Set(this.selectedItems);
      } else {
        return this._selectedItemSet || new Set(this.selectedItems);
      }
    },

    selectOverlayStyle() {
      if(this.selectRect) {
        // Bound display of selection so it doesn't cause scrolling.
        var boundedRect = boundRect(
          this.selectRect,
          this.getElemRect(this.$el.getBoundingClientRect())
        );
        return {
          left: boundedRect.left + "px",
          top: boundedRect.top  + "px",
          width: boundedRect.right - boundedRect.left + "px",
          height: boundedRect.bottom - boundedRect.top + "px",
        };
      } else {
        return {display: "none"};
      }
    },

  },
  methods: {

    /********** Helper Methods **********/

    /* Given page-coordinate (x, y), return the name of th gallery item at that
     * position, or null. */
    getItemAt(x, y) {
      for(var item of this.items) {
        var itemElement = this.$refs["item:"+item.name][0];
        if(pointInRect({x: x, y: y}, itemElement.getBoundingClientRect())) {
          return item.name;
        }
      }
      return null;
    },

    /* Given page-coordinates return the point in element coordinates. */
    getElemPoint(x, y) {
      var clientRect = this.$el.getBoundingClientRect();
      return {
        x: x - clientRect.left + this.$el.scrollLeft,
        y: y - clientRect.top + this.$el.scrollTop,
      };
    },

    /* Given page-coordinate rect, return it in element coordinates. */
    getElemRect(rect) {
      var clientRect = this.$el.getBoundingClientRect();
      return {
        left: rect.left - clientRect.left + this.$el.scrollLeft,
        right: rect.right - clientRect.left + this.$el.scrollLeft,
        top: rect.top - clientRect.top + this.$el.scrollTop,
        bottom: rect.bottom - clientRect.top + this.$el.scrollTop,
      };
    },

    /********** selectedItemSet mutation methods **********/

    selectionSet(names) {
      this._selectedItemSet = new Set(names);
      if(names.length == 0) {
        this.lastSelectedItem = null;
      } else if(names.length == 1) {
        this.lastSelectedItem = names[0];
      }
      this.selectedItemCounter++;
    },

    selectionAdd(name) {
      if(!this._selectedItemSet.has(name)) {
        this._selectedItemSet.add(name);
        this.lastSelectedItem = name;
        this.selectedItemCounter++;
      }
    },

    selectionDelete(name) {
      if(this._selectedItemSet.has(name)) {
        this._selectedItemSet.delete(name);
        this.selectedItemCounter++;
      }
    },

    selectionToggle(name) {
      if(this.oldSelectedItemSet.has(name)) {
        this.selectionDelete(name);
      } else {
        this.selectionAdd(name);
      }
    },

    /* Set reference point for selectionToggle to know if the previous
     * selection had or didn't have the item. */
    selectionStart() {
      this.oldSelectedItemSet = new Set(this._selectedItemSet);
    },

    /* Roll back to selection from last time selectionStart() was called. */
    selectionRollBack() {
      this._selectedItemSet = new Set(this.oldSelectedItemSet);
      this.selectedItemCounter++;
    },

    /********** Event Handling **********/

    onMouseDown(event) {
      if(event.button !== 0) return;
      this.ctrlKey = event.ctrlKey;
      this.shiftKey = event.shiftKey;

      // Shift-click: select all between last selected and the clicked item.
      if(this.shiftKey && this.lastSelectedItem) {
        // Only listen to shift-click if an item was clicked. Otherwise behave
        // normally.
        var itemName = this.getItemAt(event.pageX, event.pageY);
        if(itemName != null) {
          var lastSelectedIdx = this.items.findIndex(item => item.name == this.lastSelectedItem);
          var clickedIdx = this.items.findIndex(item => item.name == itemName);
          var firstIdx = Math.min(lastSelectedIdx, clickedIdx);
          var lastIdx = Math.max(lastSelectedIdx, clickedIdx);
          if(firstIdx != -1 && lastIdx != -1) {
            // Ctrl toggles items in current selection. Otherwise clear it.
            if(!this.ctrlKey) {
              this.selectionSet([]);
            }
            for(var i=firstIdx; i<=lastIdx; i++) {
              if(this.ctrlKey) {
                this.selectionToggle(this.items[i].name);
              } else {
                this.selectionAdd(this.items[i].name);
              }
            }
            // Reset last selected
            // If the user performs multiple shift-clicks in a row, we want the
            // range to start from the very initial lastSelectedItem.
            this.lastSelectedItem = this.items[lastSelectedIdx].name;
          }
          return;  // Don't drag if shift-click succeeded on an item
        }
      }

      // Set state and listeners for dragging
      this.mouseDown = true;
      this.selectStart = this.getElemPoint(event.pageX, event.pageY);
      this.selectEnd = null;
      window.addEventListener("mousemove", this.onMouseMove);
      window.addEventListener("mouseup", this.onMouseUp);

      // Clear selection if ctrl isn't held down
      if(!this.ctrlKey) {
        // If drag starts on an item, go ahead and select that item.
        var clickedItem = this.getItemAt(event.pageX, event.pageY);
        if(clickedItem !== null) {
          this.selectionSet([clickedItem]);
        } else {
          this.selectionSet([]);
        }
      }

      this.selectionStart();
    },

    onMouseMove(event) {
      if(!this.mouseDown) { return; }

      // Act like mouseUp if the mouse isn't up anymore.
      // This can happen if mouseUp happens with the mouse off the window.
      if(event.buttons != 1) {
        this.onMouseUp(event);
        return;
      }

      this.selectEnd = this.getElemPoint(event.pageX, event.pageY);

      // Find items in the select rectangle
      var itemsInRect = new Set();
      for(var item of this.items) {
        var itemElement = this.$refs["item:"+item.name][0];
        var itemRect = this.getElemRect(itemElement.getBoundingClientRect());
        if(rectIntersect(itemRect, this.selectRect)) {
          itemsInRect.add(item.name);
        }
      }

      // Update selection
      // Start by going back to the state at the beginning of the drag. Then
      // add or toggle any items in the drag rectangle.
      this.selectionRollBack();
      for(var name of itemsInRect) {
        if(this.ctrlKey) {
          this.selectionToggle(name);
        } else {
          this.selectionAdd(name);
        }
      }
    },

    onMouseUp(event) {
      if(event.button !== 0) return;

      // This is a mouse click if the mouse hasn't moved since mouse down
      // TODO: for accessability, we should probably consider it a mouse click
      //       if the mouse hasn't moved outside of the clicked item, or if
      //       onMouseUp and onMouseDown are within the same item.
      if(this.selectEnd === null) {
        var name = this.getItemAt(event.pageX, event.pageY);
        this.onItemClick(name);
      }

      // Clear state for dragging
      this.mouseDown = false;
      window.removeEventListener('mousemove', this.onMouseMove);
      window.removeEventListener('mouseup', this.onMouseUp);
      this.startPoint = null;
      this.selectEnd = null;
      this.oldSelectedItemSet = null;
    },

    onItemClick(name) {
      if(!this.ctrlKey) {
        // Clear selection, either from a click outside any item, or a click on
        // an item without ctrl held down to explicitly add to selection.
        this.selectionSet([]);
        this.lastSelectedItem = null;
      }
      if(name != null) {
        // Select or toggle clicked item
        if(this.ctrlKey) {
          this.selectionToggle(name);
        } else {
          this.selectionAdd(name);
        }
      }
    },

  },
  watch: {
    selectedItemSet() {

      // Detect if set has changed
      var changed = this.selectedItemSet.size != this.selectedItems.length;
      if(!changed) {
        for(var name of this.selectedItems) {
          if(!this.selectedItemSet.has(name)) {
            changed = true;
            break;
          }
        }
      }

      if(changed) {
        this.$emit("change", Array.from(this.selectedItemSet));
      }
    },
  },

  beforeDestroy() {
      window.removeEventListener('mousemove', this.onMouseMove)
      window.removeEventListener('mouseup', this.onMouseUp)
  },

}
</script>
