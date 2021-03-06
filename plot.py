import h5py
import subprocess
import argparse
import train
import time
import  os
import sys
import glob
import re
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description='')
parser.add_argument("-folder",default='./opt/tmp/')
parser.add_argument("-per",default=30,type = int)
parser.add_argument("-save",action='store_false', help="save pic")
parser.add_argument("-show",action='store_false', help="save pic")
parser.add_argument("-exact",type=float,default=None,help="obs_exact")
args = parser.parse_args()

rootFolder = args.folder
if rootFolder[-1] != '/':
    rootFolder += '/'

with h5py.File(rootFolder+"parameters.hdf5","r") as f:
    epochs = int(np.array(f["epochs"]))
    batch = int(np.array(f["batch"]))
    savePeriod = int(np.array(f["savePeriod"]))

plt.ion()
fig1 = plt.figure()
ax1 = fig1.add_subplot(111)
l1, = ax1.plot([], [],'o', alpha=0.5, label='direct generated')
l2, = ax1.plot([], [],'s', alpha=0.5, label='latent space hmc')
l21, = ax1.plot([], [],'*', alpha=0.5, label='physical space hmc')

plt.xlabel('$x_1$')
plt.ylabel('$x_2$')
plt.xlim([-10, 10])
plt.ylim([-10, 10])
plt.legend(loc='upper left')
fig1.canvas.draw()
fig2 = plt.figure(figsize=(8,6))
ax2 = fig2.add_subplot(311)
l3, = ax2.plot([], [], label='loss')
ax2.set_xlim([0, epochs])
ax2.legend()

ax4 = fig2.add_subplot(312)
l5, = ax4.plot([], [], 'o', label='latent space hmc accratio')
l6, = ax4.plot([], [], 'o', label='physical space hmc accratio')
ax4.set_xlim([0, epochs])
ax4.legend()

ax5 = fig2.add_subplot(313)
fig2.canvas.draw()

epoch = 0
epoch_ = 0
#tolerant0 = 1000

while(True):
    while(epoch_ == epoch):
        time.sleep(args.per/2)
        try:
            name = sorted(glob.iglob(rootFolder+"savings/*Saving*.saving"),key = os.path.getctime)[-2]
        except:
            time.sleep(args.per/2)
            '''
            tolerant0 -= 1
            if tolerant0 <=0:
                print("out of tolerant0")
                sys.exit(1)
            '''
            continue
        part = name.split('epoch')
        prefix = part[0].replace("savings","records").replace("Saving","Record")
        epoch_ = int(re.findall(r'\d+',part[1])[0])
        if epoch_ == epochs-2*savePeriod and epoch == epoch_:
            epoch_ = epochs-savePeriod
    epoch = epoch_
    print("at epoch: "+str(epoch))

    name = prefix+"epoch"+str(epoch)+".hdf5"
    with h5py.File(name,"r") as f:
        LOSS = np.array(f["LOSS"])
        XOBS = np.array(f["XOBS"])
        ZOBS = np.array(f["ZOBS"])
        XACC = np.array(f["XACC"])
        ZACC = np.array(f["ZACC"])

    name = name.replace("Record","HMCresult")
    with h5py.File(name,"r") as f:
        XZ = np.array(f["XZ"])
        X = np.array(f["X"])
        Y = np.array(f["Y"])


    X = X.reshape(batch,-1)
    l1.set_xdata(X[:,0])
    l1.set_ydata(X[:,1])

    XZ=XZ.reshape(batch,-1)
    l2.set_xdata(XZ[:,0])
    l2.set_ydata(XZ[:,1])

    Y = Y.reshape(batch,-1)
    l21.set_xdata(Y[:,0])
    l21.set_ydata(Y[:,1])
    ax1.set_title('epoch=%g'%(epoch))

    ax1.relim()
    ax1.autoscale_view()

    fig1.canvas.draw()

    l3.set_xdata(range(LOSS.shape[0]))
    l3.set_ydata(LOSS)

    l5.set_xdata(np.arange(ZACC.shape[0])*savePeriod)
    l5.set_ydata(ZACC)

    l6.set_xdata(np.arange(XACC.shape[0])*savePeriod)
    l6.set_ydata(XACC)

    ax5.cla()
    ax5.errorbar(np.arange(ZOBS.shape[0])*savePeriod, ZOBS[:,0], yerr=ZOBS[:, 1], fmt='o', capsize=8)
    ax5.errorbar(np.arange(XOBS.shape[0])*savePeriod, XOBS[:,0], yerr=XOBS[:, 1], fmt='s', capsize=8)
    if (args.exact is not None):
        plt.axhline(args.exact, color='r', lw=2)
    ax5.set_xlim([0, epochs])
    plt.xlabel('epochs')


    ax2.relim()
    ax2.autoscale_view()

    ax4.relim()
    ax4.autoscale_view()

    ax5.relim()
    ax5.autoscale_view()

    fig2.canvas.draw()

    plt.pause(0.001)

    if args.save:
        fig1.savefig(rootFolder+'pic/epoch%g.pdf'%(epoch))
        fig2.savefig(rootFolder+'pic/Loss.pdf')

    if args.show:
        plt.show()

    if epoch == epochs - savePeriod:
        print("finish with all epochs ploted")
        sys.exit(0)









