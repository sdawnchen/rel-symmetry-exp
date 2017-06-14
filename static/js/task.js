/*
 * Requires:
 *     psiturk.js
 *     utils.js
 */

// Initalize psiturk object
var psiTurk = new PsiTurk(uniqueId, adServerLoc, mode);

var mycondition = condition;  // these two variables are passed by the psiturk server process
var mycounterbalance = counterbalance;  // they tell you which condition you have been assigned to
// they are not used in the stroop code but may be useful to you

// All pages to be loaded
var pages = [
    "instructions/instructions1.html",
    "instructions/instructions2.html",
    "trial.html",
    "attn-check-trial.html",
    "saving-results.html"
];

psiTurk.preloadPages(pages);

var instructionPages = [ // add as a list as many pages as you like
    "instructions/instructions1.html",
    "instructions/instructions2.html",
];


/********************
* HTML manipulation
*
* All HTML files in the templates directory are requested 
* from the server when the PsiTurk object is created above. We
* need code to get those pages from the PsiTurk object and 
* insert them into the document.
*
********************/


function RelSimSymmetryExp() {
    var comparisons = allComps[condition];
    comparisons = _.shuffle(comparisons);

    var attnCheckQs = [
        ["representations", "simultaneously"],
        ["anthropologist", "anthropologist"],
        ["coincidence", "knowledgeable"],
        ["hummingbird", "hummingbird"]
    ];

    attnCheckQs = _.shuffle(attnCheckQs);

    var numComps = comparisons.length;
    var numAttnChecks = attnCheckQs.length;
    var numTotalQs = numComps + numAttnChecks;
    var numQsBtwnChecks = numComps / (numAttnChecks + 1);

    var trial = 0;
    var checki = 0;
    var attnCheckTrial = false;

    var sliderHandle = "#sim-rating-bar .slider-handle";
    var sliderClicked = false;

    function removeSliderTicks() {
        $("#sim-rating-bar .slider-tick.in-selection").removeClass("in-selection");
    }

    function setupTrial() {
        // Update the progress bar
        var progress = Math.round((trial + checki) / numTotalQs * 100);
        $('#progress-bar-text').html(progress + "% Complete");
        $('#progress-bar').attr({
            "aria-valuenow": progress,
            style: "width:" + progress + "%"
        });

        // Reset the slider's value to 1
        ratingSlider.setValue(1);

        // Make the slider handle invisible
        $(sliderHandle).css("visibility", "hidden");
        removeSliderTicks();
        sliderClicked = false;

        // Disable the submit button
        $("#submit").addClass("disabled");
        $("#submit").off("click");
        $("#submit").attr("title", "Please select a rating first.");

        // After a delay, fade in the second word, rating slider, and submit button
        setTimeout(function() {
            $(".initially-hidden").css('visibility','visible').hide().fadeIn("slow");
        }, 2000);

        // Record the starting time
        startTime = new Date().getTime();
    }

    function nextTrial() {
        if (attnCheckTrial) {
            // Hide the second word and everything after
            $(".initially-hidden").css('visibility', 'hidden');

            // Get the two words
            attnCheck = attnCheckQs[checki];
            $("#word1").html("<b>" + attnCheck[0] + "</b>");
            $("#word2").html("<b>" + attnCheck[1] + "</b>");

            setupTrial();
            checki++;
        } else {
            // Hide the second word pair and everything after
            $(".initially-hidden").css('visibility', 'hidden');

            // Get the two word pairs
            comp = comparisons[trial];
            $("#pair1").html("<b>" + comp[3][0] + "</b> : <b>" + comp[3][1] + "</b>");
            $("#pair2").html("<b>" + comp[4][0] + "</b> : <b>" + comp[4][1] + "</b>");

            setupTrial();
            trial++;
        }
    }

    function submit() {
        var endTime = new Date().getTime();
        var RT = endTime - startTime;
        var rating = ratingSlider.getValue();

        // If this was an attention check trial, change the page to a normal trial
        // and re-register the slider
        if (attnCheckTrial) {
            word1 = attnCheck[0];
            word2 = attnCheck[1];
            psiTurk.recordTrialData({"trial_type": "attention check",
                                     "word1": word1,
                                     "word2": word2,
                                     "rating": rating,
                                     "RT": RT});
            psiTurk.saveData();

            attnCheckTrial = false;
            psiTurk.showPage("trial.html");

            // Register the slider and its event handler
            ratingSlider = new Slider("#rating-bar");
            ratingSlider.on("slideStop", sliderClickHandler);

            nextTrial();
        
        } else {
            comp_type = comp[0];
            rel1 = comp[1];
            rel2 = comp[2];
            pair1_word1 = comp[3][0];
            pair1_word2 = comp[3][1];
            pair2_word1 = comp[4][0];
            pair2_word2 = comp[4][1];

            psiTurk.recordTrialData({"trial_type": comp_type,
                                     "relation1": rel1,
                                     "relation2": rel2,
                                     "pair1_word1": pair1_word1,
                                     "pair1_word2": pair1_word2,
                                     "pair2_word1": pair2_word1,
                                     "pair2_word2": pair2_word2,
                                     "rating": rating,
                                     "RT": RT});

            if (trial < numComps) {
                // If the next trial should be an attention check, change the page to such a
                // trial and register the slider
                if (trial % numQsBtwnChecks == 0) {
                    attnCheckTrial = true;
                    psiTurk.showPage("attn-check-trial.html");

                    // Register the slider and its event handler
                    ratingSlider = new Slider("#rating-bar");
                    ratingSlider.on("slideStop", sliderClickHandler);
                }
                nextTrial();
                
            } else {
                finish();
            }
        }
    }

    function finish() {
        psiTurk.showPage("saving-results.html");
        psiTurk.saveData();
        // Wait to close the window to make sure that the data has been sent
        setTimeout(function() { psiTurk.completeHIT(); }, 500);
    }

    function sliderClickHandler() {
        if (!sliderClicked) {
            sliderClicked = true;
            $(sliderHandle).css("visibility", "visible");
            $("#submit").removeClass("disabled");
            $("#submit").click(submit);
            $("#submit").removeAttr("title");
        }
    }

    psiTurk.recordTrialData({"condition": condition});
    
    // Load the trial.html snippet into the body of the page
    psiTurk.showPage('trial.html');


    // Register the slider and its event handler
    var ratingSlider = new Slider("#rating-bar");
    ratingSlider.on("slideStop", sliderClickHandler);

    // Show the first set of analogy questions
    nextTrial();
}


// Task object to keep track of the current phase
var currentview;

/*******************
 * Run Task
 ******************/
$(window).load( function(){
    psiTurk.doInstructions(
        instructionPages, // a list of pages you want to display in sequence
        function() { currentview = new RelSimSymmetryExp(); } // what you want to do when you are done with instructions
    );
});
