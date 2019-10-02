########
# Important parameters
########


viewing_distance = 2.0  # units can be anything so long as they match those used in screen_width below
screen_width = 1.0  # units can be anything so long as they match those used in viewing_distance above
screen_res = (1920, 1080)  # pixel resolution of the screen
# viewing_distance = 3.0 #units can be anything so long as they match those used in screen_width below
# screen_width = 1.0 #units can be anything so long as they match those used in viewing_distance above
# screen_res = (1366,768) #pixel resolution of the screen

background_noise_volume = .1

response_keys = ['z', '/']
response_triggers = [4, 5]

soa_list = [0.400, 1.600]
cue_list = ['valid', 'valid', 'valid', 'valid', 'invalid']
target_list = ['black', 'white']
signal_list = ['lo', 'hi']

fixation_min = 2.000
fixation_mean = 4.000
fixation_max = 10.000
signal_duration = 0.100
response_timeout = 1.000
ITI = 1.000

num_blocks = 12

instruction_size_in_degrees = 1  # specify the size of the instruction text
feedback_size_in_degrees = .5  # specify the size of the feedback text
target_size_in_degrees = .5  # specify the width of the target

text_width = .9  # specify the proportion of the screen to use when drawing instructions

circle_slices = 12  # specify the number of slices in the fixation/target circle

########
# Import libraries
########
import pygame
import numpy as np
import aggdraw
import math
import sys
import os
import random
import time
import shutil

########
# Start the random seed
########
seed = time.time()  # grab the current time
random.seed(seed)  # use the time to set the random seed

########
# Initialize pygame
########
sound_sample_rate = 22050
pygame.mixer.pre_init(frequency=sound_sample_rate, size=-16, channels=2, buffer=4096)

pygame.init()  # initialize pygame
pygame.mouse.set_visible(False)  # make the mouse invsoable

########
# Initialize the joystick
########
joystick = pygame.joystick.Joystick(0)
joystick.init()

########
# Initialize the screen
########

screen = pygame.display.set_mode(screen_res,
                                 pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)  # initialize a screen
screen_x_center = screen_res[0] / 2  # store the location of the screen's x center
screen_y_center = screen_res[1] / 2  # store the location of the screen's y center

########
# Perform some calculations to convert stimulus measurements in degrees to pixels
########
screen_width_in_degrees = math.degrees(math.atan((screen_width / 2.0) / viewing_distance) * 2)
PPD = screen_res[0] / screen_width_in_degrees  # compute the pixels per degree (PPD)

instruction_size = int(instruction_size_in_degrees * PPD)
feedback_size = int(feedback_size_in_degrees * PPD)

target_size = int(target_size_in_degrees * PPD)

########
# Define some useful colors
########
black = (0, 0, 0)
white = (255, 255, 255)
grey = (119, 119, 119)

########
# Initialize the fonts
########

instruction_font_size = 2
instruction_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', instruction_font_size)
instruction_height = instruction_font.size('XXX')[1]
while instruction_height < instruction_size:
    instruction_font_size = instruction_font_size + 1
    instruction_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', instruction_font_size)
    instruction_height = instruction_font.size('XXX')[1]

instruction_font_size = instruction_font_size - 1
instruction_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', instruction_font_size)
instruction_height = instruction_font.size('XXX')[1]

feedback_font_size = 2
feedback_font = pygame.font.Font('_Stimuli/DejaVuSansMono.ttf', feedback_font_size)
feedback_height = feedback_font.size('XXX')[1]
while feedback_height < feedback_size:
    feedback_font_size = feedback_font_size + 1
    feedback_font = pygame.font.Font('_Stimuli/DejaVuSansMono.ttf', feedback_font_size)
    feedback_height = feedback_font.size('XXX')[1]

feedback_font_size = feedback_font_size - 1
feedback_font = pygame.font.Font('_Stimuli/DejaVuSansMono.ttf', feedback_font_size)
feedback_height = feedback_font.size('XXX')[1]

feedback_eraser_size = feedback_font.size('XXXXXXX\nXXXXXXX\nXXXXXXX')
feedback_eraser = pygame.Surface((feedback_eraser_size[0], feedback_eraser_size[1]))
feedback_eraser.fill(grey)


########
# Create sprites for visual stimuli
########

# define a function to turn PIL/aggdraw images to pygame surfaces
def image2surf(image):
    mode = image.mode
    size = image.size
    data = image.tobytes()
    return pygame.image.fromstring(data, size, mode)


white_circle = aggdraw.Draw('RGBA', [target_size, target_size], grey)
white_circle.ellipse([0, 0, target_size, target_size], aggdraw.Brush(white))
white_circle = image2surf(white_circle)

black_circle = aggdraw.Draw('RGBA', [target_size, target_size], grey)
black_circle.ellipse([0, 0, target_size, target_size], aggdraw.Brush(black))
black_circle = image2surf(black_circle)

circle_eraser = pygame.Surface((target_size * 2, target_size * 2))
circle_eraser.fill(grey)

# create cue sprites
short_cue = feedback_font.render('S', True, [0, 0, 255])
long_cue = feedback_font.render('L', True, [0, 0, 255])


########
# Helper functions
########

# define a function to draw a pygame surface centered on given coordinates
def blit_to_screen(surf, x_offset=0, y_offset=0):
    x = screen_x_center + x_offset - surf.get_width() / 2.0
    y = screen_y_center + y_offset - surf.get_height() / 2.0
    screen.blit(surf, (x, y))


# define a function to return the pygame time in seconds
def pytime():
    return time.time()  # pygame.time.get_performance_counter()/1000000.0


# define a function that waits for a given duration to pass
def simple_wait(duration):
    start = pytime()
    while pytime() < (start + duration):
        pass


# define a function that formats text for the screen
def draw_text(my_text, instruction_font, text_color, my_surface, text_width):
    my_surface_rect = my_surface.get_rect()
    text_width_max = int(my_surface_rect.size[0] * text_width)
    paragraphs = my_text.split('\n')
    render_list = []
    text_height = 0
    for this_paragraph in paragraphs:
        words = this_paragraph.split(' ')
        if len(words) == 1:
            render_list.append(words[0])
            if (this_paragraph != paragraphs[len(paragraphs) - 1]):
                render_list.append(' ')
                text_height = text_height + instruction_font.get_linesize()
        else:
            this_word_index = 0
            while this_word_index < (len(words) - 1):
                line_start = this_word_index
                line_width = 0
                while (this_word_index < (len(words) - 1)) and (line_width <= text_width_max):
                    this_word_index = this_word_index + 1
                    line_width = instruction_font.size(' '.join(words[line_start:(this_word_index + 1)]))[0]
                if this_word_index < (len(words) - 1):
                    # last word went over, paragraph continues
                    render_list.append(' '.join(words[line_start:(this_word_index - 1)]))
                    text_height = text_height + instruction_font.get_linesize()
                    this_word_index = this_word_index - 1
                else:
                    if line_width <= text_width_max:
                        # short final line
                        render_list.append(' '.join(words[line_start:(this_word_index + 1)]))
                        text_height = text_height + instruction_font.get_linesize()
                    else:
                        # full line then 1 word final line
                        render_list.append(' '.join(words[line_start:this_word_index]))
                        text_height = text_height + instruction_font.get_linesize()
                        render_list.append(words[this_word_index])
                        text_height = text_height + instruction_font.get_linesize()
                    # at end of paragraph, check whether a inter-paragraph space should be added
                    if (this_paragraph != paragraphs[len(paragraphs) - 1]):
                        render_list.append(' ')
                        text_height = text_height + instruction_font.get_linesize()
    num_lines = len(render_list) * 1.0
    for this_line in range(len(render_list)):
        this_render = instruction_font.render(render_list[this_line], True, text_color)
        this_render_rect = this_render.get_rect()
        this_render_rect.centerx = my_surface_rect.centerx
        this_render_rect.centery = int(
            my_surface_rect.centery - text_height / 2.0 + 1.0 * this_line / num_lines * text_height)
        my_surface.blit(this_render, this_render_rect)


# define a function that will kill everything safely
def exit_safely():
    pygame.quit()
    try:
        data_file.close()
    except:
        pass
    sys.exit()


# define a function that waits for a response
def wait_for_response(key=None):
    pygame.event.clear()
    done = False
    while not done:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                response = event.unicode
                if response == '\x1b':
                    exit_safely()
                else:
                    if key == None:
                        done = True
                    elif response == key:
                        done = True
    pygame.event.clear()
    return response


# define a function that prints a message on the screen while looking for user input to continue. The function
# returns the total time it waited
def show_message(my_text, key=None):
    message_viewing_time_start = pytime()
    pygame.event.pump()
    pygame.event.clear()
    screen.fill(black)
    pygame.display.flip()
    screen.fill(black)
    draw_text(my_text, instruction_font, grey, screen, text_width)
    simple_wait(.5)
    pygame.display.flip()
    screen.fill(black)
    wait_for_response(key=key)
    pygame.display.flip()
    screen.fill(black)
    simple_wait(.5)
    message_viewing_time = pytime() - message_viewing_time_start
    return message_viewing_time


# define a function that requests user input
def get_input(get_what):
    get_what = get_what + '\n'
    text_input = ''
    screen.fill(black)
    pygame.display.flip()
    simple_wait(.5)
    my_text = get_what + text_input
    screen.fill(black)
    draw_text(my_text, instruction_font, grey, screen, text_width)
    pygame.display.flip()
    screen.fill(black)
    done = False
    while not done:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key_down = event.unicode
                if key_down == '\x1b':
                    exit_safely()
                elif key_down == '\x7f':
                    if text_input != '':
                        text_input = text_input[0:(len(text_input) - 1)]
                        my_text = get_what + text_input
                        screen.fill(black)
                        draw_text(my_text, instruction_font, grey, screen, text_width)
                        pygame.display.flip()
                elif key_down == '\r':
                    done = True
                else:
                    text_input = text_input + key_down
                    my_text = get_what + text_input
                    screen.fill(black)
                    draw_text(my_text, instruction_font, grey, screen, text_width)
                    pygame.display.flip()
    screen.fill(black)
    pygame.display.flip()
    return text_input


# define a function that obtains subject info via user input
def get_sub_info():
    year = time.strftime('%Y')
    month = time.strftime('%m')
    day = time.strftime('%d')
    hour = time.strftime('%H')
    minute = time.strftime('%M')
    sid = get_input('ID:')
    if sid != 'test':
        age = get_input('Age (2-digit number):')
        handedness = get_input('Handedness (r or l):')
        sex = get_input('Sex (m or f):')
    else:
        sex = 'test'
        age = 'test'
        handedness = 'test'
        languages = 'test'
        music = 'test'
        gaming = 'test'
    sub_info = [sid, year, month, day, hour, minute, sex, age, handedness]
    return sub_info


# define a function that initializes the data file
def initialize_data_files():
    if not os.path.exists('_Data'):
        os.mkdir('_Data')
    if sub_info[0] == 'test':
        filebase = 'test'
    else:
        filebase = '_'.join(sub_info[0:6])
    if not os.path.exists('_Data/' + filebase):
        os.mkdir('_Data/' + filebase)
    shutil.copy(__file__, '_Data/' + filebase + '/' + filebase + '_code.py')
    data_file_name = '_Data/' + filebase + '/' + filebase + '_data.txt'
    data_file = open(data_file_name, 'w')
    header = '\t'.join(
        ['id', 'year', 'month', 'day', 'hour', 'minute', 'sex', 'age', 'handedness', 'wait', 'block', 'trial_num',
         'fixation_interval', 'soa', 'cue', 'signal', 'target', 'rt', 'response', 'error', 'pre_target_response',
         'ITI_response'])
    data_file.write(header + '\n')
    trigger_file_name = '_Data/' + filebase + '/' + filebase + '_trigger.txt'
    trigger_file = open(trigger_file_name, 'w')
    header = '\t'.join(
        ['id', 'year', 'month', 'day', 'hour', 'minute', 'sex', 'age', 'handedness', 'block', 'trial_num', 'signal',
         'trigger', 'time', 'value'])
    trigger_file.write(header + '\n')
    return data_file, trigger_file


# define a function to generate a fixation interval
def get_fixation_interval():
    fixation_interval = random.expovariate(1 / (fixation_mean - fixation_min)) + fixation_min
    while fixation_interval > fixation_max:
        fixation_interval = random.expovariate(1 / (fixation_mean - fixation_min)) + fixation_min
    return fixation_interval


# define a function that generates a randomized list of trial-by-trial stimulus information representing a factorial
# combination of the independent variables.
def get_trials(block):
    trials = []
    for soa in soa_list:
        for target in target_list:
            for cue in cue_list:
                for signal in signal_list:
                    fixation_interval = get_fixation_interval()
                    trials.append([fixation_interval, soa, cue, target, signal])
    random.shuffle(trials)
    return trials


# define a function that runs a block of trials
def run_block(block, message_viewing_time):

    # get a trial list
    trial_list = get_trials(block)
    trial_num = 0

    # start running trials
    while len(trial_list) > 0:
        # bump the trial number
        trial_num = trial_num + 1

        # parse the trial info
        fixation_interval, soa, cue, target, signal = trial_list.pop(0)

        # generate the sound arrays
        max_int = 2 ** 16 / 4
        pre_cue = np.random.randint(-max_int, max_int, int(fixation_interval * sound_sample_rate))
        if signal == 'hi':
            signal_multiplier = 2
        else:
            signal_multiplier = 1
        cue_L = np.random.randint(-max_int * signal_multiplier, max_int * signal_multiplier,
                                  int(signal_duration * sound_sample_rate))
        cue_R = np.random.randint(-max_int * signal_multiplier, max_int * signal_multiplier,
                                  int(signal_duration * sound_sample_rate))
        post_cue = np.random.randint(-max_int, max_int, 10 * sound_sample_rate)
        L = np.concatenate((pre_cue, cue_L, post_cue))
        R = np.concatenate((pre_cue, cue_R, post_cue))
        arr = np.c_[L, R]
        try:
            snd.stop()
        except:
            pass
        snd = pygame.sndarray.make_sound(arr.astype(np.int16))
        snd.play(1)
        pygame.event.pump()

        if cue == 'valid':
            if soa == soa_list[0]:
                cue_stim = short_cue
            else:
                cue_stim = long_cue
        else:
            if soa == soa_list[0]:
                cue_stim = long_cue
            else:
                cue_stim = short_cue

        done = False
        while not done:
            if pygame.mixer.get_busy():
                done = True

        # start the trial by showing the fixation screen
        screen.fill(grey)
        blit_to_screen(cue_stim)
        pygame.display.flip()  # this might not block
        screen.fill(grey)
        blit_to_screen(cue_stim)
        pygame.display.flip()  # this should block

        pygame.event.clear()

        # get the trial start time and compute event times
        trial_start_time = pytime() - 1 / 60.00  # one frame in the past
        cue_on_time = trial_start_time + fixation_interval
        cue_off_time = cue_on_time + signal_duration
        target_on_time = cue_on_time + soa
        target_off_time = target_on_time + response_timeout

        # prep the target screen
        screen.fill(grey)
        if target == 'white':
            blit_to_screen(white_circle)
        else:
            blit_to_screen(black_circle)

        # prep some variables
        pre_target_response = 'FALSE'
        ITI_response = 'FALSE'
        response = 'NA'
        rt = 'NA'
        error = 'NA'
        cue_started = False
        cue_done = False
        target_started = False
        target_done = False
        trial_done = False
        left_trigger_vals = []
        right_trigger_vals = []
        while not trial_done:
            if not target_started:
                if pytime() >= target_on_time:
                    target_started = True
                    pygame.display.flip()
            elif not target_done:
                if pytime() >= target_off_time:
                    target_done = True
                    trial_done = True
                    response = 'NA'
                    error = 'NA'
                    rt = 'NA'
                    feedback_text = 'Miss!'
                    feedback_color = [255, 0, 0]
                    ITI_done_time = target_off_time + ITI
            pygame.event.pump()
            now = pytime() - target_on_time
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis in response_triggers:
                        if event.axis == response_triggers[0]:
                            left_trigger_vals.append([now, event.value])
                        else:
                            right_trigger_vals.append([now, event.value])
                        if event.value > 0:
                            trial_done = True
                            if not target_started:
                                ITI_done_time = now + ITI
                                trial_done = True
                                pre_target_response = 'TRUE'
                                feedback_text = 'Too soon!'
                                feedback_color = [255, 0, 0]
                            else:
                                response = event.axis
                                rt = now
                                feedback_text = str(int(round(rt * 10)))
                                ITI_done_time = pytime() + ITI
                                if response == black_response:
                                    response = 'black'
                                elif response == white_response:
                                    response = 'white'
                                else:
                                    feedback_color = [255, 0, 0]
                                    feedback_text = 'wrong keys!'
                                if target == 'black':
                                    feedback_color = black
                                elif target == 'white':
                                    feedback_color = white
                                if response == target:
                                    error = 'FALSE'
                                elif ((response == 'black') or (response == 'white')):
                                    error = 'TRUE'
                                else:
                                    error = 'NA'
                elif event.type == pygame.KEYDOWN:
                    trial_done = True
                    if event.unicode == '\x1b':
                        exit_safely()
                    elif not target_started:
                        ITI_done_time = now + ITI
                        trial_done = True
                        pre_target_response = 'TRUE'
                        feedback_text = 'Too soon!'
                        feedback_color = [255, 0, 0]
                    else:
                        response = event.unicode
                        rt = now
                        feedback_text = str(int(round(rt * 10)))
                        ITI_done_time = pytime() + ITI
                        if response == black_response:
                            response = 'black'
                        elif response == white_response:
                            response = 'white'
                        else:
                            feedback_color = [255, 0, 0]
                            feedback_text = 'wrong keys!'
                        if target == 'black':
                            feedback_color = black
                        elif target == 'white':
                            feedback_color = white
                        if response == target:
                            error = 'FALSE'
                        elif ((response == 'black') or (response == 'white')):
                            error = 'TRUE'
                        else:
                            error = 'NA'

        # present the feedback screen
        blit_to_screen(circle_eraser)
        rendered_feedback_text = feedback_font.render(feedback_text, True, feedback_color)
        blit_to_screen(rendered_feedback_text)
        pygame.display.flip()

        while pytime() < ITI_done_time:
            pygame.event.pump()
            now = pytime() - target_on_time
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis in response_triggers:
                        if event.axis == response_triggers[0]:
                            left_trigger_vals.append([now, event.value])
                        else:
                            right_trigger_vals.append([now, event.value])
                elif event.type == pygame.KEYDOWN:
                    if event.unicode == '\x1b':
                        exit_safely()
                    else:
                        if feedback_text == 'Miss!':
                            feedback_text = 'Too slow!'
                        else:
                            feedback_text = 'Too many!'
                        ITI_response = 'TRUE'
                        ITI_done_time = pytime() + ITI
                        blit_to_screen(feedback_eraser)
                        rendered_feedback_text = feedback_font.render(feedback_text, True, [255, 0, 0])
                        blit_to_screen(rendered_feedback_text)
                        pygame.display.flip()

        # write out data
        for i in left_trigger_vals:
            trial_info = '\t'.join(map(str, [sub_info_for_file, block, trial_num, signal, 'left', i[0], i[1]]))
            trigger_file.write(trial_info + '\n')
        for i in right_trigger_vals:
            trial_info = '\t'.join(map(str, [sub_info_for_file, block, trial_num, signal, 'right', i[0], i[1]]))
            trigger_file.write(trial_info + '\n')
        trial_info = '\t'.join(map(str,
                                   [sub_info_for_file, message_viewing_time, block, trial_num, fixation_interval, soa,
                                    cue, signal, target, rt, response, error, pre_target_response, ITI_response]))
        data_file.write(trial_info + '\n')
    snd.stop()


########
# Start the experiment
########

# get subject info
sub_info = get_sub_info()
sub_info_for_file = '\t'.join(map(str, sub_info))

# initialize the data file
data_file, trigger_file = initialize_data_files()

black_response = response_triggers[0]
white_response = response_triggers[1]

message_viewing_time = show_message(
    'In this experiment your job is to watch for the appearance of white and black circles. \nWhen either circle '
    'appears, press down on both the left and right triggers of the gamepad. \nWhen the circles appear, '
    'try to respond as quickly as you can. Try not to make too many errors, like responding too early, but responding '
    'quickly is most important.\nWhen you are ready to proceed to the next page of instructions, press the "Y" key.',
    'y')

message_viewing_time = show_message(
    'To help you monitor how quickly and accurately you\'re responding, a number will appear showing how long it took '
    'you to respond (in tenths of a second). You want this number to be as SMALL as possible, ideally between 2 and '
    '6.\nWhen you are ready to proceed to the next page of instructions, press the "Y" key.',
    'y')

message_viewing_time += show_message(
    'Throughout the experiment you will hear a fuzz sound through the headphones. We would like for the volume to be '
    'the same for everyone, so try not to adjust this. If you need to reduce or increase the volume, please let the '
    'experimentor know and they will change it for you.\nThe fuzz sound will change slightly before the circles '
    'appear, providing you with a warning to get ready for the circles.\nWhen you are ready to proceed to the next '
    'page of instructions, press the "Y" key.',
    'y')

message_viewing_time += show_message(
    'Sometimes the circles will appear immediately after this warning, but sometimes it will take a moment for the '
    'circles to appear. Before the warning occurs, a letter will appear that indicates whether it will be a short '
    'time ("S") between the warning and circle, or if it will be a long time ("L") between the warning and circle. '
    'Please use the length information while doing the task as this will benefit your performance. \nWhen you are '
    'ready to proceed to the next page of instructions, press the "Y" key.',
    'y')

message_viewing_time += show_message(
    'To give you a feel for how the experiment works, the first few minutes will be considered '
    'practice.\n\nRemember:\nRespond by pressing BOTH triggers down.\nThe "S" means "short" and the "L" means "long". '
    'Use these letters to help you respond as quick as possible.\n\nWhen you are ready to begin practice, '
    'press "Y" key.',
    'y')

run_block(block='practice', message_viewing_time=message_viewing_time)
message_viewing_time = show_message(
    'Practice is complete.\nWhen you are ready to continue to the experiment, press the "Y" key.', 'y')
for i in range(num_blocks):
    block = i + 1
    run_block(block=block, message_viewing_time=message_viewing_time)
    if block < num_blocks:
        message_viewing_time = show_message('Take a break!\nYou are ' + str(block) + '/' + str(
            num_blocks) + ' done the experiment.\nWhen you are ready to resume the experiment, press the "Y" key.', 'y')

message_viewing_time = show_message(
    'You\'re all done!\nPress the "Y" key to quit the experiment, after which you are free to quietly use your phone '
    'or the computuer. The experimentor will let you know when everyone is done and you can leave',
    'y')

exit_safely()
