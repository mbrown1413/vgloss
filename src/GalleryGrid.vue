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
          :class="{'gallery-item-selected': selectedItems.has(item.name)}"
        >
          <div
            class="gallery-item-image"
            :style="{backgroundImage: 'url('+item.image+')'}"
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
    height: 100%;
  }
  .gallery-items {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    grid-gap: 1rem;
    align-items: center;
    padding: 0.5em;
    user-select: none;
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
     * https://stackoverflow.com/questions/1495407/maintain-the-aspect-ratio-of-a-div-with-css
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
    // One rect is to left/right of other
    rect1.left >= rect2.right || rect2.left >= rect1.right ||
    // One rect is to above/below other
    rect1.top >= rect2.bottom || rect2.top >= rect1.bottom
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
 * TODO: Not yet implemented:
 *   * Click with shift held down to select only items between the last
 *     selected item and the clicked item.
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
  },
  data() {
    return {
      mouseDown: false,
      selectStart: null,
      selectEnd: null,
      selectedItemCounter: 1,
    };
  },
  created() {
    // Since Vue can't react to Set changes, we do a bit of a hack here. The
    // counter selectedItemCounter will increment whenever we add/remove items.
    // _selectedItems contains the actual set, while the computed property
    // selectedItems can be used as normal. Of course, you have to increment
    // the counter whenever _selectedItems changes.
    // TODO: Support for watching Sets is planned for Vue 3!
    //       https://github.com/vuejs/vue/issues/2410
    this._selectedItems = new Set();
  },
  computed: {
    selectRect() {
      if(this.mouseDown && this.selectStart && this.selectEnd) {
        return boundRect(
          {
            left:   Math.min(this.selectStart.x, this.selectEnd.x),
            right:  Math.max(this.selectStart.x, this.selectEnd.x),
            top:    Math.min(this.selectStart.y, this.selectEnd.y),
            bottom: Math.max(this.selectStart.y, this.selectEnd.y),
          },
          this.$el.getBoundingClientRect()
        );
      } else {
        return null;
      }
    },
    selectOverlayStyle() {
      if(this.selectRect) {
        return {
          display: "block",
          left: this.selectRect.left + "px",
          top: this.selectRect.top + "px",
          width: this.selectRect.right - this.selectRect.left + "px",
          height: this.selectRect.bottom - this.selectRect.top + "px",
        };
      } else {
        return {display: "none"};
      }
    },
    selectedItems() {
      if(this.selectedItemCounter > -1) {
        return this._selectedItems;
      } else {
        return this._selectedItems;
      }
    },
  },
  methods: {
    getItemAt(x, y) {
      for(var item of this.items) {
        var itemElement = this.$refs["item:"+item.name][0];
        if(pointInRect({x: x, y: y}, itemElement.getBoundingClientRect())) {
          return item.name;
        }
      }
      return null;
    },
    onMouseDown(event) {
      if(event.button !== 0) return;

      // Set state and listeners for dragging
      this.mouseDown = true;
      this.selectStart = {
        x: event.pageX,
        y: event.pageY,
      };
      this.selectEnd = null;
      window.addEventListener("mousemove", this.onMouseMove);
      window.addEventListener("mouseup", this.onMouseUp);

      // Clear selection if ctrl isn't held down
      if(event.ctrlKey) {
        this.selectToggle = true;
      } else {
        this.selectToggle = false;
        this._selectedItems.clear();
        // If drag starts on an item, go ahead and select that item.
        var clickedItem = this.getItemAt(event.pageX, event.pageY);
        if(clickedItem) {
          this._selectedItems.add(clickedItem);
        }
        this.selectedItemCounter++;
      }

      // Keep old selection behind for reference. If we didn't clear it,
      // selectToggle will add/remove from the oldSelectedItems.
      this.oldSelectedItems = new Set(this.selectedItems);
    },
    onMouseMove(event) {
      if(!this.mouseDown) { return; }

      this.selectEnd = {
        x: event.pageX,
        y: event.pageY,
      };

      // Find items in the select rectangle
      var itemsInRect = new Set();
      for(var item of this.items) {
        var itemElement = this.$refs["item:"+item.name][0];
        var itemRect = itemElement.getBoundingClientRect();
        if(rectIntersect(itemRect, this.selectRect)) {
          itemsInRect.add(item.name);
        }
      }

      // Update selection
      // Use oldSelectedItems from when the drag started and modify it
      // accordingly.
      this._selectedItems = new Set(this.oldSelectedItems);
      for(var name of itemsInRect) {
        if(this.selectToggle && this.oldSelectedItems.has(name)) {
          this._selectedItems.delete(name);
        } else {
          this._selectedItems.add(name);
        }
      }
      this.selectedItemCounter++;
    },
    onMouseUp() {
      if(event.button !== 0) return;

      // This is a mouse click if the mouse hasn't moved since mouse down
      if(this.selectEnd === null) {
        var name = this.getItemAt(event.pageX, event.pageY);
        this.onItemClick(name, event);
      }

      // Clear state for dragging
      this.mouseDown = false;
      window.removeEventListener('mousemove', this.onMouseMove)
      window.removeEventListener('mouseup', this.onMouseUp)
      this.startPoint = null;
      this.selectEnd = null;
      this.oldSelectedItems = null;
    },
    onItemClick(name, event) {
      if(!event.ctrlKey) {
        this._selectedItems = new Set();
      }
      if(name) {
        if(this.selectToggle && this.oldSelectedItems.has(name)) {
          this._selectedItems.delete(name);
        } else {
          this._selectedItems.add(name);
        }
      }
      this.selectedItemCounter++;
    },
  },
  beforeDestroy() {
      window.removeEventListener('mousemove', this.onMouseMove)
      window.removeEventListener('mouseup', this.onMouseUp)
  },
}
</script>
