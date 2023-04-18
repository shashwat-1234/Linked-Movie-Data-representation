(function () {
  var width,
    height,
    largeHeader,
    canvas,
    ctx,
    points,
    target,
    animateHeader = true;

  // Main
  initHeader();
  initAnimation();
  addListeners();

  function initHeader() {
    width = window.innerWidth;
    height = window.innerHeight;
    // target = { x: width / 2, y: height / 2 };

    largeHeader = document.getElementById("large-header");
    largeHeader.style.height = height + "px";

    // for each point find the 5 closest points
    // for (var i = 0; i < points.length; i++) {
    //   var closest = [];
    //   var p1 = points[i];
    //   for (var j = 0; j < points.length; j++) {
    //     var p2 = points[j];
    //     if (!(p1 == p2)) {
    //       var placed = false;
    //       for (var k = 0; k < 5; k++) {
    //         if (!placed) {
    //           if (closest[k] == undefined) {
    //             closest[k] = p2;
    //             placed = true;
    //           }
    //         }
    //       }

    //       for (var k = 0; k < 5; k++) {
    //         if (!placed) {
    //           if (getDistance(p1, p2) < getDistance(p1, closest[k])) {
    //             closest[k] = p2;
    //             placed = true;
    //           }
    //         }
    //       }
    //     }
    //   }
    //   p1.closest = closest;
    // }

    // assign a circle to each point
    // for (var i in points) {
    //   var c = new Circle(
    //     points[i],
    //     2 + Math.random() * 2,
    //     "rgba(255,255,255,0.3)"
    //   );
    //   points[i].circle = c;
    // }
  }

  // Event handling
  function addListeners() {
    if (!("ontouchstart" in window)) {
      window.addEventListener("mousemove", mouseMove);
    }
    window.addEventListener("scroll", scrollCheck);
    window.addEventListener("resize", resize);
  }

  function mouseMove(e) {
    var posx = (posy = 0);
    if (e.pageX || e.pageY) {
      posx = e.pageX;
      posy = e.pageY;
    } else if (e.clientX || e.clientY) {
      posx =
        e.clientX +
        document.body.scrollLeft +
        document.documentElement.scrollLeft;
      posy =
        e.clientY +
        document.body.scrollTop +
        document.documentElement.scrollTop;
    }
    target.x = posx;
    target.y = posy;
  }

  function scrollCheck() {
    if (document.body.scrollTop > height) animateHeader = false;
    else animateHeader = true;
  }

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    largeHeader.style.height = height + "px";
    canvas.width = width;
    canvas.height = height;
  }
})();
