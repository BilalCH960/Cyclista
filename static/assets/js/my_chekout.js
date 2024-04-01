
// $(document).ready(function () {
//     // Add change event listener to both select elements
//     $("#select_ship, #select_bill").change(function () {
//         // Check if both shipping and billing addresses are selected
//         if ($("#select_ship").val() && $("#select_bill").val()) {
//             // Enable the "Place Order" button
//             $("#placeOrderBtn").prop("disabled", false);
//         } else {
//             // Disable the "Place Order" button
//             $("#placeOrderBtn").prop("disabled", true);
//         }
//     });
// });


    var payment;
    var shippingAddressId;
    var billingAddressId;

    function mess(){
        Swal.fire({
            icon: 'Info',
            title: 'Please wait',
            text: 'Please hang in there for a while',
        });
    }
    function getSelectedPaymentOption() {
        var radioButtons = document.querySelectorAll('input[name="payment_option"]');
    
        for (var i = 0; i < radioButtons.length; i++) {
            console.log('RadioButton:', radioButtons[i].id, 'Checked:', radioButtons[i].checked);

            if (radioButtons[i].checked) {
                payment = radioButtons[i].id;
                console.log('Selected payment option:', payment);

                if (payment == 'exampleRadios3'){
                    $('#seamPayDiv').show();
                    console.log(seam)
                }
                else{
                    $('#seamPayDiv').hide();
                    console.log(seam)

                }
                break;
            }
        }
    }
    $(document).ready(function() {
        $('input[name="payment_option"]').prop('checked', false);
        $('#exampleRadios3').prop('checked', false);

        function openAddress() {
            $('#my_address_form').toggle($('#flexCheckChecked').prop('checked'));
        }
        $('#flexCheckChecked').change(openAddress);

        openAddress();
    });



    var seam = 0;
    $('#seampay').change(function (){
        if(seam == 0){
            seam = 1
        }
        else{
            seam = 0 
        }
    }); 

    


    // function place_order() {
    //     var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
    //     console.log('Data being sent:', {
    //         'shipping': shippingAddressId,
    //         'billing': billingAddressId,
    //         'payment_select': payment,
    //         'the seam val': seam,
    //         'csrfmiddlewaretoken': csrfToken
    //     });

    //     if (payment == 'exampleRadios6') {
    //         $.ajax({
    //             url: "place_order",
    //             method: "POST",
    //             dataType: 'json',
    //             data: {
    //                 'shipping': shippingAddressId,
    //                 'billing': billingAddressId,
    //                 'payment_select': payment,
    //                 'csrfmiddlewaretoken': csrfToken
    //             },
    //             success: function (data) {
    //                 if (data.success) {
    //                     console.log(date.success + 'hello')
    //                     Swal.fire({
    //                         icon: 'success',
    //                         title: 'Hooray',
    //                         text: 'The order has been placed successfully',
    //                     });
    //                     window.location.href = 'order_placed_view';
    //                 } else {
    //                     Swal.fire({
    //                         icon: 'warning',
    //                         title: 'Please select Your address',
    //                         text: 'Select your Billing or shipping address',
    //                     });
    //                 }
    //             },
    //         });
    //     }
    // }


        
  