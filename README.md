# Overview

This is the code for Experiment 2 (violations of symmetry in relational similarity judgments) in "Evaluating vector-space models of analogy" (Chen, Peterson, & Griffiths, to appear in the *CogSci 2017 Proceedings*). You can download the paper [here](https://arxiv.org/abs/1705.04416). The code uses [psiTurk](https://psiturk.org/).


# Screenshots

Here is an example trial:

![Example relational symmetry trial](https://github.com/sdawnchen/rel-symmetry-exp/blob/master/screenshots/trial.png)

Note that the 600 ms delay before the appearance of the second word pair has already passed in this example. The `screenshots` folder also contains screenshots of the instruction pages.


# Stimuli Details

The stimuli come from the [SemEval-2012 Task 2 dataset](https://sites.google.com/site/semeval2012task2/), as described in the paper. The included `get_stimuli.py` will create new random stimuli for the experiment from the SemEval dataset and save them in the file `static/js/SemEval-stimuli.js`. After randomly selecting 1,000 relational similarity stimuli as described in the paper, the code creates 20 random subsets of them so that each participant only has to rate 50 stimuli (under certain constraints, such as a participant never seeing both the forward and backward directions of a comparison) and each comparison is rated a roughly equal number of times. Each participant is randomly assigned to one of the 20 subsets.


# Dependencies/Credits

All dependencies for the online experiment (not the code for getting the stimuli, which requires the SemEval dataset) have been included. These include [psiTurk](https://psiturk.org/), [jQuery](https://jquery.com/), [Underscore](http://underscorejs.org/), [Backbone](http://backbonejs.org/), [D3](https://d3js.org/), [Bootstrap](http://getbootstrap.com/), and [bootstrap-slider](http://seiyria.com/bootstrap-slider/).
