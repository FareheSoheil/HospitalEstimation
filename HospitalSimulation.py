from numpy import random
import random as rand
from math import ceil,exp
from heapq import heappush, heappop
import matplotlib.pyplot as plt
TYPE1=1
TYPE2=2
THRESHOLDS = [0,10,5]
PRIORITIES={
	'A':['A','B','C'],
	'B':['B','C','A'],
	'C':['C','B','A']
}
FRANSHIZ=[0.2,0.5,0.8]
BEDSNUMBER={
	'A':2,
	'B':4,
	'C':3
}
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	Magenta = '\u001b[35m'
	Cyan = '\u001b[36m'
class Patient:
	def __init__(self,kind,stayingTime,Ci,insurance,cameAt):
		self.kind = kind
		self.stayingTime=stayingTime
		self.Ci = -1 * Ci
		self.insurance = insurance
		self.cameAt=cameAt
class PatientOnCi(Patient):
	def __lt__(self,other):
		return self.Ci < other.Ci
class PatientOnTi(Patient):
	def __init__(self,kind,stayingTime,Ci,insurance,cameAt):
		super().__init__(kind,stayingTime,Ci,insurance,cameAt)
		self.stayingTime=-1*stayingTime
	def __lt__(self,other):
		return self.stayingTime < other.stayingTime		
class Bed:	
	def __init__(self, status,freeFrom,hospital,patientType):
		self.status = status
		self.freeFrom = freeFrom
		self.hospital=hospital
		self.patientType=patientType
class Screening:
	def __init__(self,p1,p2,slots):
		self.p1=p1
		self.p2=p2
		self.slots=slots
		self.optMech = {
			'patList':[], #keeps patients with positive Ci in discending order
			'inQ':[],
			'bedList':[], #keeps beds and their assignment according to opt mechanism
			'income': {
				'A': 0,
				'B': 0,
				'C': 0
				},
			'deads':0,
			'currentWaitingPats':0,
			'payment':0
		}
		self.stableMatch = {
			'patList':[], #keeps all patient
			'bedList':[] ,#keeps all beds
			'income':{
				'A': 0,
				'B': 0,
				'C': 0
				},
			'deads':0,
			'currentWaitingPats':0,
			'payment':0
		}
		self.allWaitingPatsFromBegining=0
		self.allComingPats=0
		self.initBeds()
	def initBeds(self):
		for x in range(0,2):
			self.optMech['bedList'].append(Bed(1,1,'A',0))
			self.stableMatch['bedList'].append(Bed(1,1,'A',0))
		for x in range(0,4):
			self.optMech['bedList'].append(Bed(1,1,'B',0))
			self.stableMatch['bedList'].append(Bed(1,1,'B',0))
		for x in range(0,3):
			self.optMech['bedList'].append(Bed(1,1,'C',0))
			self.stableMatch['bedList'].append(Bed(1,1,'C',0))
	def exponentialDistrib(self,kind):	
		return random.exponential(scale=10/kind)	
	def emptyBedProbablityGenerator(self,kind):
		return (1-exp(-0.1*kind))
	def deathProbablityGenerator(self,kind):
		return (1-exp(-0.1*kind))
		# if(deathProb<=1- exp(-0.5 * kind)):
	def C(self,t,kind) :
		if(kind==1):
			return t-10
		else:
			return t-5
	def patientArrivalCheck(self,rp1,rp2,t): #CHECKED 
		# print("\n********************************** Patients Information at Slot(",t,") ******************************\n")
		if(rp1<=self.p1) : #patient type 1 has arrived
			self.allComingPats = self.allComingPats+1
			self.patientInfoGenerator(1,t)
		if(rp2<=self.p2) : #patient type 2 has arrived
			self.allComingPats = self.allComingPats+1
			self.patientInfoGenerator(2,t)
	def patientInfoGenerator(self,kind,t):
		t=self.exponentialDistrib(kind) #generate his staying time 
		c=self.C(t,kind) #calculate Ci
		insurProb=random.uniform(0,1) #generate insurance type
		insurType='A'
		if(insurProb>0.2 and insurProb<=0.5) : 
			insurType='B'
		elif(insurProb>0.5 and insurProb<=1):
			insurType='C'
		pat1 = PatientOnTi(kind,t,c,insurType,t) #instantiate the patient sorted on Ti
		pat2 = PatientOnCi(kind,t,c,insurType,t) #instantiate the patient sorted on Ci
		heappush(self.stableMatch['patList'],pat1) #add him to the stable matching list
		self.stableMatch['currentWaitingPats'] = self.stableMatch['currentWaitingPats'] + 1
		# print(f"{bcolors.OKGREEN}patient type {kind} has come and t:  {t}	{bcolors.ENDC}")
		if(c>0): #let him wait for opt mechanism if worth it
			# print("and he stays for opt mechanism ")
			heappush(self.optMech['patList'], pat2) #add him to the opt mechanism list
			self.optMech['currentWaitingPats'] = self.optMech['currentWaitingPats'] + 1
			self.allWaitingPatsFromBegining = self.allWaitingPatsFromBegining + 1
		else : 
			self.optMech['inQ'].append(pat2)


	def emptyBedChecker(self,goal):
		emptyBedsNumber = 0
		emptyBedsList=[]
		# check if any bed disembouges
		if(goal=='opt') : 
			for i in range(0,9):
				if(self.optMech['bedList'][i].status == 0):
					# print("bed ",i," with patient kind : ",self.optMech['bedList'][i].patientType, " is full")
					r=random.uniform(0,1)
					# print(r," and ",self.emptyBedProbablityGenerator(self.optMech['bedList'][i].patientType))
					if(r<=self.emptyBedProbablityGenerator(self.optMech['bedList'][i].patientType)):
						# print("but is free now")
						self.optMech['bedList'][i].status = 1
						emptyBedsList.append(i)
						emptyBedsNumber = emptyBedsNumber+1
				else : 
					emptyBedsList.append(i)
					emptyBedsNumber = emptyBedsNumber+1
			return emptyBedsNumber,emptyBedsList
		else:
			for i in range(0,9):
				if(self.stableMatch['bedList'][i].status == 0):
					# print("bed ",i," with patient kind : ",self.stableMatch['bedList'][i].patientType, " is full")
					r=random.uniform(0,1)
					# print(r," and ",self.emptyBedProbablityGenerator(self.stableMatch['bedList'][i].patientType))
					if(r<=self.emptyBedProbablityGenerator(self.stableMatch['bedList'][i].patientType)):
						# print("but is free now")
						self.stableMatch['bedList'][i].status=1
						emptyBedsNumber = emptyBedsNumber+1
				else : 
					emptyBedsNumber = emptyBedsNumber+1
			return emptyBedsNumber
	def optimalMechanism(self,t,option):
		emptyBedsNumber=0
		counter = 0
		condition = 0
		miu = 0
		eligiblePats=[]
		# count empty beds
		emptyBedsNumber,emptyBedsList=self.emptyBedChecker('opt')
		# Update Patients' Ci in Q (negative Cis)
		size= len(self.optMech['inQ'])
		i=0
		while (size>0 and i<size):
			if(self.optMech['inQ'][i].cameAt!=t):
				newT=self.exponentialDistrib(self.optMech['inQ'][i].kind)
				newC=self.C(newT,self.optMech['inQ'][i].kind)
				
				if(newC>0):#if new Ci is positive add this patient to the list
					# print("patient is renewed , newC is : ", newC)
					self.optMech['inQ'][i].Ci=-1*newC
					heappush(self.optMech['patList'],self.optMech['inQ'][i])
					del self.optMech['inQ'][i]
					size=size-1
					self.optMech['currentWaitingPats'] = self.optMech['currentWaitingPats'] + 1
				else:
					i=i+1
			else:
				i=i+1

		if(self.optMech['currentWaitingPats']>0 and self.optMech['currentWaitingPats'] <= emptyBedsNumber) : 
			counter = self.optMech['currentWaitingPats']
			condition = 1
		elif (emptyBedsNumber>0 and self.optMech['currentWaitingPats']>emptyBedsNumber) :
			counter = emptyBedsNumber
			condition = 2
		# print(f"{bcolors.FAIL}empty beds at slot {t} are: {emptyBedsNumber} and waiting patients are {self.optMech['currentWaitingPats']}{bcolors.ENDC}")
		# find the eligible patients
		while counter > 0:
				pat = heappop(self.optMech['patList'])
				self.optMech['currentWaitingPats'] = self.optMech['currentWaitingPats']-1
				eligiblePats.append(pat)
				counter = counter-1 
		# give bed to eligible patients
		if(condition != 0):
			randomBeds = rand.sample(range(emptyBedsNumber),len(eligiblePats))
			for i in randomBeds:
				# give the bed to the patient
				self.optMech['bedList'][emptyBedsList[i]].status=0
				self.optMech['bedList'][emptyBedsList[i]].patientType = eligiblePats[counter].kind
				emptyBedsNumber=emptyBedsNumber-1
				# print(f"{bcolors.OKBLUE}bed {emptyBedsList[i]} from hospital {self.optMech['bedList'][emptyBedsList[i]].hospital} is assigned to patient with ci = {eligiblePats[counter].Ci * -1} with kind {self.optMech['bedList'][emptyBedsList[i]].patientType} and remaining beds # is : {emptyBedsNumber}{bcolors.ENDC}")
				if(condition == 1) : #There are no apponents
					miu = THRESHOLDS[eligiblePats[counter].kind]
				elif(condition == 2) :
					pat = heappop(self.optMech['patList']) #can't have Ci less than this
					heappush(self.optMech['patList'], pat)
					ci = pat.Ci * -1
					miu = THRESHOLDS[eligiblePats[counter].kind] + ci
					
				self.optMech['payment'] = self.optMech['payment'] + miu 
				self.optMech['income'][self.optMech['bedList'][emptyBedsList[i]].hospital] = self.optMech['income'][self.optMech['bedList'][emptyBedsList[i]].hospital] + miu
				counter = counter + 1
		if(option==1):
			tmpList=[]
			#check patients in this list for death :)
			while self.optMech['patList']:
				pat=heappop(self.optMech['patList'])
				deathProb=random.uniform(0,1)
				if(deathProb<=self.deathProbablityGenerator(pat.kind)): #patient dies
					self.optMech['deads'] = self.optMech['deads'] + 1
					# print("HE DIES in opt")
					self.optMech['currentWaitingPats'] = self.optMech['currentWaitingPats']-1
				else:
					heappush(tmpList,pat)
			size = len(self.optMech['inQ'])
			cnt=0
			#check patients in this list for death :)
			while size>0 and cnt<size:
				deathProb=random.uniform(0,1)
				if(deathProb<=self.deathProbablityGenerator(self.optMech['inQ'][cnt].kind)): #patient dies
					# print("len(self.optMech['inQ']) : ",len(self.optMech['inQ']))	
					del self.optMech['inQ'][cnt]
					size=size-1
					self.optMech['deads'] = self.optMech['deads'] + 1
					# print("HE DIES in opt")
				else:
					cnt=cnt+1

			self.optMech['patList']=tmpList
	def stableMatching(self,t,option):
		emptyBedsNumber=0
		payment=0
		eligiblePats=[]
		emptyBedsNumber = self.emptyBedChecker('matching')
		o=w = min(emptyBedsNumber,self.stableMatch['currentWaitingPats'])
		# if(emptyBedsNumber<=self.stableMatch['currentWaitingPats']):
		# print("w is : ",emptyBedsNumber,"  ",self.stableMatch['currentWaitingPats'])
		# print("watings is : ",self.stableMatch['currentWaitingPats'])
		while w>0: #enough number of patients with highest staying time
			pat=heappop(self.stableMatch['patList'])
			eligiblePats.append(pat)
			self.stableMatch['currentWaitingPats'] = self.stableMatch['currentWaitingPats']-1
			w=w-1
		# print(f"{bcolors.FAIL}empty beds at slot {t} are: {emptyBedsNumber} and waiting patients are {o} {bcolors.ENDC}")
		for i in range(0,len(eligiblePats)):
			priorityList=PRIORITIES[eligiblePats[i].insurance]
			cnt=0
			flg=0
			while cnt<3:	
				for j in range(0,9):
					if(self.stableMatch['bedList'][j].status==1):
						if(self.stableMatch['bedList'][j].hospital==priorityList[cnt]):
							# update bed
							self.stableMatch['bedList'][j].status=0
							self.stableMatch['bedList'][j].patientType = eligiblePats[i].kind
							# print(f"{bcolors.OKBLUE}bed {j} from hospital {self.stableMatch['bedList'][j].hospital} is assigned to patient with kind {self.stableMatch['bedList'][j].patientType} and insurance {eligiblePats[i].insurance} and remaining beds # is : {emptyBedsNumber-1}{bcolors.ENDC}")
							# compute payment 
							payment = (eligiblePats[i].stayingTime*-1) * FRANSHIZ[cnt]
							self.stableMatch['payment']=self.stableMatch['payment']+payment
							self.stableMatch['income'][priorityList[cnt]]=self.stableMatch['income'][priorityList[cnt]]+(eligiblePats[i].stayingTime*-1)
							emptyBedsNumber=emptyBedsNumber-1
							flg=1
							cnt=3
							break
				if(flg==0):
					cnt=cnt+1

		if(option==1):
			tmpList=[]
			while self.stableMatch['patList']:
				pat=heappop(self.stableMatch['patList'])
				deathProb=random.uniform(0,1)
				# print("in death : ",deathProb,"  ",1- exp(-0.5 * pat.kind))
				if(deathProb<= self.deathProbablityGenerator(pat.kind)): #patient dies
					self.stableMatch['deads'] = self.stableMatch['deads'] + 1
					# print("HE DIES in matching")
					self.stableMatch['currentWaitingPats'] = self.stableMatch['currentWaitingPats']-1
				else:
					heappush(tmpList,pat)
			self.stableMatch['patList']=tmpList
	def assignment(self,option):
		rp1=0
		rp2=0
		for x in range(1,self.slots+1):
			# checking wether any patient has arrived
			rp1=random.uniform(0,1)
			rp2=random.uniform(0,1)
			self.patientArrivalCheck(rp1,rp2,x)
			self.stableMatching(x,option)
			self.optimalMechanism(x,option)

probs=[]
optMech={
		'payment' : [],
		'incomeA':[],
		'incomeB':[],
		'incomeC':[],
		'AllIncomes':[],
		'deads':[]
		}
matching={
		'payment' : [],
		'incomeA':[],
		'incomeB':[],
		'incomeC':[],
		'AllIncomes':[],
		'deads':[]
		}
comings=[]
slots=10000
# sc = Screening(1,1,slots)
# sc.assignment(1)
# print("**************************************************************")
# print(sc.optMech['payment'])
# print(sc.stableMatch['payment'])

for x in range(1,10):
	p2 = 1/x
	p1=1/(1.3*x)
	probs.append(p2)
	sc = Screening(p2,p1,slots)
	sc.assignment(1)	
	optMech['payment'].append(sc.optMech['payment']/slots),
	optMech['AllIncomes'].append((sc.optMech['income']['A']+sc.optMech['income']['B']+sc.optMech['income']['C'])/slots),
	optMech['incomeA'].append(sc.optMech['income']['A']/slots),
	optMech['incomeB'].append(sc.optMech['income']['B']/slots),
	optMech['incomeC'].append(sc.optMech['income']['C']/slots),
	optMech['deads'].append(sc.optMech['deads']/slots)
	matching['payment'].append(sc.stableMatch['payment']/slots),
	matching['AllIncomes'].append((sc.stableMatch['income']['A']+sc.stableMatch['income']['B']+sc.stableMatch['income']['C'])/slots),
	matching['incomeA'].append(sc.stableMatch['income']['A']/slots),
	matching['incomeB'].append(sc.stableMatch['income']['B']/slots),
	matching['incomeC'].append(sc.stableMatch['income']['C']/slots),
	matching['deads'].append(sc.stableMatch['deads']/slots)
	comings.append(sc.allComingPats)

for x in range(0,9):
	print("probs : ",probs[x])
	print("All of the patients : ",comings[x])
	print(f"{bcolors.Magenta}OPT MECHANISM  : ____________________{bcolors.ENDC}")
	print(optMech['payment'][x],"\n")
	print(f"{bcolors.Cyan}MATCHING MECHANISM  : ____________________ {bcolors.ENDC}")
	print(matching['payment'][x],"\n")
	print("_____________________________________________________________")

plt.figure(1)#Payment
plt.plot(probs,optMech['payment'],"y-*")
plt.plot(probs,matching['payment'],"r-h")
plt.xlabel('Patient arrival prob. (P2, P1=P2/1.3)') 
plt.ylabel('Average of Patients Payments')   
plt.title('Green : opt mechanism, Red: matching, Time Slots : 10000')
plt.figure(2)#Hospital A income
plt.plot(probs,optMech['incomeA'],"y-*")
plt.plot(probs,matching['incomeA'],"r-h")
plt.xlabel('Patient arrival prob. (P2, P1=P2/1.3)') 
plt.ylabel('Average of  Hospital A income')   
plt.title('Green : opt mechanism, Red: matching, Time Slots : 10000')
plt.figure(3) #Hospital B income
plt.plot(probs,optMech['incomeB'],"y-*")
plt.plot(probs,matching['incomeB'],"r-h")
plt.xlabel('Patient arrival prob. (P2, P1=P2/1.3)') 
plt.ylabel('Average of  Hospital B income')   
plt.title('Green : opt mechanism, Red: matching, Time Slots : 10000')
plt.figure(4) #Hospital C income
plt.plot(probs,optMech['incomeC'],"y-*")
plt.plot(probs,matching['incomeC'],"r-h")
plt.xlabel('Patient arrival prob. (P2, P1=P2/1.3)') 
plt.ylabel('Average of  Hospital C income')   
plt.title('Green : opt mechanism, Red: matching, Time Slots : 10000')
plt.figure(5)#Deads
plt.plot(probs,optMech['deads'],"y-*")
plt.plot(probs,matching['deads'],"r-h")
plt.xlabel('Patient arrival prob. (P2, P1=P2/1.3)')
plt.ylabel('Average of Deaths')   
plt.title('Green : opt mechanism, Red: matching, Time Slots : 10000')
plt.figure(6)# average of all oncomes
plt.plot(probs,optMech['AllIncomes'],"y-*")
plt.plot(probs,matching['AllIncomes'],"r-h")
plt.xlabel('Patient arrival prob. (P2, P1=P2/1.3)')
plt.ylabel('Average of All Incomes ')   
plt.title('Green : opt mechanism, Red: matching, Time Slots : 10000')
plt.show()	