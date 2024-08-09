function galleryOpenModal() {
  document.getElementById("galleryModal").style.display = "block";
}

function galleryCloseModal() {
  document.getElementById("galleryModal").style.display = "none";
}

let slideIndex = 1;
galleryShowSlide(slideIndex);

function galleryNextSlide(n) {
    galleryShowSlide(slideIndex += n);
}

function galleryCurrentSlide(n) {
    galleryShowSlide(slideIndex = n);
}

function galleryShowSlide(n) {
  let i;
  let slides = document.getElementsByClassName("gallerySlide");
  let thumbs = document.getElementsByClassName("galleryThumb");
  let credits = document.getElementsByClassName("galleryCredits");
  let captions = document.getElementsByClassName("galleryCaption");
  let captionText = document.getElementById("gallerySlideCaption");
  let creditsText = document.getElementById("gallerySlideCredits");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
  }
  for (i = 0; i < thumbs.length; i++) {
    thumbs[i].className = thumbs[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";
  thumbs[slideIndex-1].className += " active";
  captionText.innerHTML = captions[slideIndex-1].innerHTML;
  creditsText.innerHTML = credits[slideIndex-1].innerHTML;
}
