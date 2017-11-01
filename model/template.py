import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class RealNVPtemplate():
    def __init__(self,sList,tList,prior,name=None):
        self.tList = tList
        self.tNumLayers = len(self.tList)
        self.sList = sList
        self.sNumLayers = len(self.sList)
        assert self.sNumLayers == self.tNumLayers
        self.NumLayers = self.sNumLayers
        self.prior=prior
        if name is None:
            self.name = "realNVP_" + str(self.sNumLayers)+"inner_"+"_layers_"+self.prior.name+"Prior"
        else:
            self.name = name
    def _generate(self,y,mask):
        self._logjac = Variable(torch.zeros(y.data.shape[0]))
        mask_ = 1-mask
        for i in range(self.sNumLayers):
            if i%2 == 0:
                y_ = mask*y
                tmp = self.sList[i](y_)
                y = y_+mask_*(y*torch.exp(tmp)+self.tList[i](y_))
                self._logjac += tmp.sum(dim=1)
            else:
                y_ = mask_*y
                tmp = self.sList[i](y_)
                y = y_+mask*(y*torch.exp(tmp)+self.tList[i](y_))
                self._logjac += tmp.sum(dim=1)
        return y,mask
    def _inference(self,y,mask):
        mask_ = 1-mask
        for i in list(range(self.sNumLayers))[::-1]:
            if (i%2==0):
                y_ = mask*y
                tmp = self.sList[i](y_)
                y = mask_*(y-self.tList[i](y_))*torch.exp(-tmp)+y_
            else:
                y_ = mask_*y
                tmp = self.sList[i](y_)
                y = mask*(y-self.tList[i](y_))*torch.exp(-tmp)+y_
        return y,mask
    def _logProbability(self,x,mask):
        z,_ = self._inference(x,mask)
        return self.prior.logProbability(z).sum(dim=1) + self._logjac
    def _saveModel(self,saveDic):
        # save is done some where else, adding s,t to the dict
        for i in range(self.sNumLayers):
            saveDic["__"+str(i)+'sLayer']=self.sList[i].state_dict()
            saveDic["__"+str(i)+'tLayer']=self.tList[i].state_dict()
        return saveDic
    def _loadModel(self,saveDic):
        #load is done some where else, pass the dict here.
        for i in range(self.sNumLayers):
            self.sList[i].load_state_dict(saveDic["__"+str(i)+'sLayer'])
            self.tList[i].load_state_dict(saveDic["__"+str(i)+'tLayer'])
        return saveDic

class PriorTemplate():
    def __init__(self,name="prior"):
        self.name = name
    def __call__(self):
        raise NotImplementedError(str(type(self)))
    def logProbability(self,x):
        raise NotImplementedError(str(type(self)))

if __name__ == "__main__":

    # Examples for tempalte

    class Gaussian(PriorTemplate):
        def __init__(self,numVars,name = "gaussian"):
            super(Gaussian,self).__init__(name)
            self.numVars = numVars
        def __call__(self,batchSize):
            return torch.randn(batchSize,self.numVars)
        def logProbability(self,z):
            return -0.5*(z**2)

    class Mlp(nn.model):
        def __init__(self,inNum,outNum,hideNum,name="mlp"):
            super(Mlp, self).__init__()
            self.fc1 = nn.Linear(inNum,hideNum)
            self.fc2 = nn.Linear(hideNum,outNum)
            self.name = name
        def forward(self,x):
            x = self.fc1(x)
            x = F.relu(x)
            x = self.fc2(x)
            return x

    class RealNVP(RealNVPtemplate):
        def __init__(self,sList,tList,prior):
            super(RealNVP,self).__init__(sList,tList,dataShape)

    gaussian = Gaussian(2)

    sList = [Mlp(1,1,10),Mlp(1,1,10),Mlp(1,1,10),Mlp(1,1,10)]
    tList = [Mlp(1,1,10),Mlp(1,1,10),Mlp(1,1,10),Mlp(1,1,10)]

    realNVP = RealNVP(sList,tList,gaussian)
