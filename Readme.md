A music generation system that generates compositions consisting of melodies and chords. 
The generated music is output as a MIDI-file. 

# Representation

In order to generate structured music, the system utilizes different hierarchical structures to represent different musical aspects: 

* Metric representation. Expresses how the music behaves in time domain, much like sheet notation. 
    - Consists of a sequence of Bars, which contain either 3 or 4 Beats, which are then divided into 4 quarter beats.
    
* Abstract, hierarchically grouped representation:
    - A full composition consists of a sequence of Sections, which each contain a melody and a chord sequence.
    - Melodies consist of motifs, which then consist of notes. 
    - Chord Sequences consist of chords, which then consist of notes.

# Generation
The generative process is conducted by the top-level module "Composer". First, general characteristics such as tempo, scale, and general structure (sequence of sections on a form like ABAC" is generated. 
Then, instructive parameters for the generation process are generated. These are contained in the dictionaries "chord_info", "metric_info", and "melodic_info".
Upon generating each section, these dictionaries are passed to the constructor of the Section object. For each new section, some of these remain the same, and some change. 
This is to ensure both cohesion and variation. For instance, the Composer module modifies what is known as the "main_motif" in "melodic_info", upon the creation of a new Section. The main motif is used as a sort of building block to creater larger melodies in the Section module. By transforming the original main motif in such a way that it retains similarities to the main motif of previous sections, melodic cohesion throughout the entire composition is ensured. In general, the Composer module works to ensure that repetition occurs on multiple structural levels, such as motifs, melodies, chord sequences and full sections. Similarly, it also works towards keeping the mapping from abstract representation to metric representation consistent but varied throughout the generation of each section.

Each section is generated based on instructions from the composer module. These instructions determine how to melody should be generated in the abstract hierarchical representation, and how it should be mapped to metric representation. Melodies are generated as a series of transformations of a main motif. Once a melody has been generated in the metric representation, it is passed to the Harmonizer module, which generates a chord sequence by formulating the harmonization problem as a Constraint Satisfaction Problem. 

Once each section is generated, their metric representations are concatenated and transformed to MIDI-representation, which is analogous to performing a piece of music from sheet notation. 

# greatest hits:

https://www.youtube.com/watch?v=fjEDNnID0U0


The system uses the following libraries:

MIDIUtil: https://pypi.org/project/MIDIUtil/

python-constraint: https://pypi.org/project/python-constraint/
