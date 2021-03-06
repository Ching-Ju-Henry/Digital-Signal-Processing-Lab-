# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 17:21:09 2017

@author: Jimmy
"""

import numpy as np
import math
from scipy.fftpack import dct 
from scipy.fftpack import idct 
import scipy.io.wavfile as wav
from numpy import linalg
from matplotlib import mlab
import soundfile as sf
from scipy.fftpack import fft, ifft
import wave 
import pyaudio
import matplotlib.pyplot as plt

#pre-emphasis
def pre_emphasis(signal,coefficient=0.95):
    return np.append(signal[0],signal[1:]-coefficient*signal[:-1])

def mel2hz(mel):
    '''
    mel scale to Hz scale
    '''
        ###################
        #design it
        ##################
    hz = 700*(10**(mel/2595.0)-1)
    return hz

def hz2mel(hz):
    '''
    hz scale to mel scale
    '''
        ###################
        #design it
        ##################
    mel = 2595*np.log10(1+hz/700.0)
    return mel

def get_filter_banks(filters_num,NFFT,samplerate,low_freq=0,high_freq=None):
    ''' Mel Bank
    filers_num: filter numbers
    NFFT:points of your FFT
    samplerate:sample rate
    low_freq: the lowest frequency that mel frequency include
    high_freq:the Highest frequency that mel frequency include
    '''
    #turn the hz scale into mel scale
    low_mel=hz2mel(low_freq)
    high_mel=hz2mel(high_freq)
    #in the mel scale, you should put the position of your filter number 
    mel_points=np.linspace(low_mel,high_mel,filters_num+2)
    #get back the hzscale of your filter position
    hz_points=mel2hz(mel_points)
    #Mel triangle bank design
    bin=np.floor((NFFT+1)*hz_points/samplerate)
    fbank=np.zeros([filters_num,int(NFFT/2+1)])
    for m in range (1, 1+filters_num):
        fm_min = int(bin[m-1]) #left
        fm = int(bin[m])       #center
        fm_max = int(bin[m+1]) #right
        
        for k in range(fm_min, fm):
            fbank[m-1, k] = (k-bin[m-1])/(bin[m]-bin[m-1])
        for k in range(fm, fm_max):
            fbank[m-1, k] = (bin[m+1]-k)/(bin[m+1]-bin[m])
        ###################
        #design it
        ##################
    return fbank

for k in range (10):
    #reading signal
    filena = '/home/henry/DSP/train1/%d.wav'%(k)
    
    signal,fs = sf.read(filena)
    
    #setting parameter
    fs=fs                               #SampleRate
    signal_length=len(signal)           #Signal length
    win_length= 0.025                    #Window_size
    win_step= 0.01                     #Window_hop
    frame_length=int(win_length*fs)     #Frame length 
    frame_step=int(win_step*fs)         #Step length
    emphasis_coeff= 0.95                 #pre-emphasis para
    filters_num= 5                  #Filter number

    NFFT= 512 #256
    low_freq=0
    high_freq=int(fs/2)



    #STFT
    frames_num=1+int(math.ceil((1.0*signal_length-frame_length)/frame_step))
    #padding    
    pad_length=int((frames_num-1)*frame_step+frame_length)  
    zeros=np.zeros((pad_length-signal_length,))          
    pad_signal=np.concatenate((signal,zeros))   
    #split into frames
    indices=np.tile(np.arange(0,frame_length),(frames_num,1))+np.tile(np.arange(0,frames_num*frame_step,frame_step),(frame_length,1)).T  
    indices=np.array(indices,dtype=np.int32) 
    frames=pad_signal[indices] 
    frames *= np.hamming(frame_length)

    #FFT and abs
    complex_spectrum=np.fft.rfft(frames,NFFT).T
    absolute_complex_spectrum=np.abs(complex_spectrum)


    #create triangular filter and plot it
    fb=get_filter_banks(filters_num,NFFT,fs,low_freq,high_freq)
    plt.figure(3)
    plt.title('fb')
    for i in range(filters_num):
         plt.plot(fb[i])

    #signal inner product with triangular filter
    feat = np.dot(np.transpose(absolute_complex_spectrum),np.transpose(fb))
    feat = np.where(feat == 0, np.finfo(float).eps, feat)
    feat = np.log(feat)

    #Apply DCT
    feat=dct(feat, norm='ortho')[:,:filters_num]
    


    print (feat.shape)
    final = 'train_%d.npy'%(k+30)
    np.save(final, feat)

    

