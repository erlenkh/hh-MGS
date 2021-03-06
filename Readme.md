A music generation system that generates compositions consisting of melodies and chords. The system's design is based on the principle of hierarchical hybridization 
 as suggested by [Carnovalini and Roda](https://www.researchgate.net/publication/340411945_Computational_Creativity_and_Music_Generation_Systems_An_Introduction_to_the_State_of_the_Art). The generated music is output as a MIDI-file. 

# Representation
In order to generate structured music, it the system utilizes different hierarchical structures to represent different musical aspects: 

* Metric representation. Expresses music in the time domain, much like sheet notation. 
    - Consists of a sequence of Bars, which contain either 3 or 4 Beats, which are then divided into 4 quarter beats.
    
* Abstract, hierarchically grouped representation:
    - A full composition consists of a sequence of Sections, which each contain a Melody and a Chord Sequence.
    - Melodies consist of Motifs, which consist of Notes. 
    - Chord Sequences consist of Chords, which consist of Notes.

# Generation
The generative process is conducted by the top-level module "Composer". This module creates a sequence of Section objects, and a set of generative instructions. These instructions are passed to the constructor of each Section. They inform how the Section's melody and chords are generated, and how they are transformed to Metric representation, i.e. the timing and rhythm. The composer is in charge of ensuring both cohesion and variation, by varying some of the generative instructions from section to section, while keeping some consistent. For instance, how the melody instructions should change from section to section is stored in a dictionary called melodic outline. 

The melody of each Section is generated on the basis of a main motif, passed from the Composer. This main motif is then copied and transformed (based on intructions from Composer) in order generate a full melodic hierarchy. Once a melody has been generated as a melody hierarchy, it is mapped to metric representation, and passed to the Harmonizer module, which generates a chord sequence by formulating the harmonization problem as a Constraint Satisfaction Problem. 

Once each section is generated, their metric representations are concatenated and transformed to MIDI-representation, which is analogous to performing a piece of music from sheet notation.

# greatest hits:

https://www.youtube.com/watch?v=fjEDNnID0U0

# External libraries:

The system uses the following libraries:

MIDIUtil: https://pypi.org/project/MIDIUtil/

python-constraint: https://pypi.org/project/python-constraint/
