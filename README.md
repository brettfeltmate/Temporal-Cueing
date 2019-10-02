# Temporal-Cueing
Experimental code for an extension of McCormick, C. R., Redden, R. S., Lawrence, M. A., & Klein, R. M. (2018). The independence of endogenous and exogenous temporal attention. Attention, Perception, & Psychophysics, 80(8), 1885-1891.

This version includes a blocked memory load manipulation, that is, in 1/2 of blocks trials begin with the presentation of an list of 5 single digit numbers. At the end of each trial (in memory load blocks) the participant is shown one number, and must respond whether (or not) it was included in the list presented at the beginning of the trial.

Additionally, where the original version randomly sampled fixation duration from an exponential distribution bounded between 2 & 10s (M=4s), this version samples from a range of 1 to 5s (M=2s).

Original version uploaded September 24th, 2019 to github.com/TheKleinLab/Temporal-Cueing

To launch, open terminal, change your directory to that of the experiment file (i.e., 'cd ~/Path/To/Temporal-Cueing-Directory/'), and type 'python mixed_detection_code.py'. If you are looking to demo the experiment, input 'test' (no quotes) as ID when asked.


