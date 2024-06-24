const monthNames = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sept","Oct","Nov","Dec" ];


// $("#commentForm").submit(function(e){
//   e.preventDefault();

//   let dt = new Date();
//   let time = dt.getDay() + " " + monthNames[dt.getUTCMonth()] + "," + dt.getFullYear()

//   $.ajax({
//     data : $(this).serialize(),

//     method : $(this).attr("method"),

//     url : $(this).attr("action"),

//     dataType : "json",

//     success : function(response){
//       console.log("saved to db")

//       if(response.bool == true){
//         $("#review-res").html("Review added successfully.")
//         $(".hide-comment-form").hide()
//         $(".add-review").hide()

//         let _html = '<div class="single-comment justify-content-between d-flex mb-">'
//             _html += '<div class="user justify-content-between d-flex">'
//             _html += '<div class="thumb text-center">'

//             _html += '<img src='+ response.context.img +' alt="">'
                         
//             _html += '<h6>'+ response.context.user +'</h6>'
//             _html += '</div>'
//             _html += '<div class="desc">'
            
//             for(let i = 1; i <= response.context.rating; i++){
//               _html += '<i class = "fas fa-star text-warning"></i>'
//             }

//             _html += '<p>'+ response.context.review +'</p>'
//             _html += '<div class="d-flex justify-content-between">'
//             _html += '<div class="d-flex align-items-center">'
//             _html += '<p class="font-xs mr-30">'+ time +'</p>'
//             _html += '</div>'
//             _html += '</div>'
//             _html += '</div>'
//             _html += '</div>'
//             _html += '</div>' 
//             $(".comment-list").prepend(_html)
//       }
//     }
//   })
// })

;$(document).ready(function (){
  function filterProducts(page = 1) {
    let filter_object = {}

    $(".filter-checkbox").each(function(){
        let filter_key = $(this).data("filter");
        filter_object[filter_key] = Array.from(document.querySelectorAll('input[data-filter='+ filter_key +']:checked')).map(function(element){
            return element.value;
        });
    });

    filter_object['sort_by'] = $('input[name="sort_by"]:checked').val();
    filter_object['page'] = page;

    $.ajax({
        url: '/filter-product',
        data: filter_object,
        dataType: 'json',
        beforeSend: function(){
            console.log("filtering products");
        },
        success: function(response){
            console.log(response);
            console.log("Data filtered successfully");
            $("#filtered-product").html(response.data);
            $("#pagination").html(response.pagination);
            updatePaginationLinks(); // Reinitialize pagination links
        }
    });
}

$(".filter-checkbox").on("click", function(){
    filterProducts();
});

$('input[name="sort_by"]').on("change", function() {
    filterProducts();
});

function updatePaginationLinks() {
  $(document).off("click", ".pagination a"); // Remove previous event handlers
  $(document).on("click", ".pagination a", function(e) {
      e.preventDefault();
      let page = $(this).attr('href').split('page=')[1];
      filterProducts(page);
  });
}

updatePaginationLinks();
});

