let investmentsCalculator = (function() {
   let startEl, endEl, amountEl;
   let ids = {
/*    input: {
         start: 'investment-start-score',
         end: 'investment-end-score',
         amount: 'investment-amount'
      },
      output: 'investment-result', */
      button: 'investment-calc'
   }
   function init(){
      let calcButton = document.getElementById(ids.button);
      calcButton.addEventListener('click', e=> calc() );
   }
   // formula functions are converted to JS from formula.py
   // the function names follow the paper on memes.market
   // parameter names also follow the paper, except for start and end, which replace v0 and vf for consistency with other parts of this code
   function linear_interpolate(x, x_0, x_1, y_0, y_1){
     let m = (y_1 - y_0) / x_1 - x_0;
     let c = y_0;
     let y = (m * x) + c;
     return y;
   }
   function S(x, max, mid, stp){
      let arg = -(stp * (x - mid));
      let y = max / (1 + Math.exp(arg));
      return y;
   }
   function gain(start, end) {
      if(end < start) {
        // treat negative gain as no gain
        return 0;
      }
      else {
        return end - start;
      }
   }
   function max(start) {
      return 1.2 + 1.4 / ((start / 7) + 1);
   }
   function mid(start) {
      let sig_mp_0 = 7;
      let sig_mp_1 = 500;
      return linear_interpolate(start, 0, 25000, sig_mp_0, sig_mp_1);
   }
   function stp(start){
      return 0.01 / ((start / 100) + 1);
   }
   function C(start, end) {
     return S(gain(start, end), max(start), mid(start), stp(start));
   }
   function calc(){
      let start = parseInt(document.getElementById('investment-start-score').value);
      let end = parseInt(document.getElementById('investment-end-score').value);
      let amount = parseInt(document.getElementById('investment-amount').value);
      if(start>=0 && end>=0 && amount >= 100){
         //creates a spinning loader
         document.getElementById('investment-result').innerHTML =
         `<div class="preloader-wrapper small active custom-preloader-wrapper">
          <div class="spinner-layer spinner-yellow-only">
            <div class="circle-clipper left">
              <div class="circle"></div>
            </div><div class="gap-patch">
              <div class="circle"></div>
            </div><div class="circle-clipper right">
              <div class="circle"></div>
            </div>
          </div>
         </div>`
         let factor = C(start, end);
         let output = (amount * factor).toFixed();
         output = isNaN(output)?"invalid data":output;
         output = (output+[]).length>20?formatToUnits(output):output;
         //replaces the spinning loader with the calculated result
         document.getElementById('investment-result').innerText = output;
      }else{
         document.getElementById('investment-result').innerText = 'invalid data';
         let toastHTML = 'you have to fill all the fields with a valid number'
         if(amount<100){
            toastHTML = 'you can\'t invest less than 100 M¢'
         }
         M.toast({html: toastHTML,displayLength:2000, classes:"dark-toast"}); 
      }
   }
   return {
      init: init
   }
})();



(function(){
   document.addEventListener('DOMContentLoaded', function(){
      //init local modules
      investmentsCalculator.init();
      M.AutoInit();
   });
}());





