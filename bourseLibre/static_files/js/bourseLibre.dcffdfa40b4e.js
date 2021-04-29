$(document).ready(function() {
//
//  $('[data-toggle="offcanvas"]').click(function() {
//    $('#wrapper').toggleClass('toggled');
//  });
//
//  // Toggle the class
//  $('body').on('click', '.dropdown', function() {
//    $(this).toggleClass('show');
//  });


   $('.quantite-right-plus').click(function(e){
        // Stop acting like a button
        e.preventDefault();
        // Get the field name
        var quantite = parseFloat($('#quantite').val());
        
        // If is not undefined
            $('#quantite').val(quantite + 1);  // Increment
        
    });

     $('.quantite-left-minus').click(function(e){
        // Stop acting like a button
        e.preventDefault();
        // Get the field name
        var quantite = parseFloat($('#quantite').val());

            if(quantite>1){
             $('#quantite').val(quantite - 1);
            }
    });


   $('.bouton_recherche').click(function(e){
        // Stop acting like a button
        // e.preventDefault();
        var recherche = $('#recherche').val();
        location.href="/search/?"+recherche;

    });
});

(function(){
    $('bouton_rechercher').click(function(e) {
        var recherche = $('#recherche').val();
        location.href="/search/?"+recherche;
    });

    if ($('#scroll-to-top').length) {
		var scrollTrigger = 100, // px
			backToTop = function () {
				var scrollTop = $(window).scrollTop();
				if (scrollTop > scrollTrigger) {
					$('#scroll-to-top').addClass('show');
				} else {
					$('#scroll-to-top').removeClass('show');
				}
			};
		backToTop();
		$(window).on('scroll', function () {
			backToTop();
		});
		$('#scroll-to-top').on('click', function (e) {
			e.preventDefault();
			$('html,body').animate({
				scrollTop: 0
			}, 700);
		});
	}

})
//$(function() {
//   $('button').click(function() {
//        var quantite = parseInt($('#quantite').val());
//        location.href="/panier/ajouter"
//   });
//});
//$(function() {
//   $('buttonAjouterAuPanier').click(function() {
//        var quantite = parseFloat($('#quantite').val());
//        location.href="/panier/ajouter"
//   });
//});