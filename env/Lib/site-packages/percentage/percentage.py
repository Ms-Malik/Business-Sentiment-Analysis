class etc:
	def __init__(self):
		return None
	dice=[1,2,3,4,5,6]
	coin=[0,1]
class percentage:
	def __init__(self):
		return None
	def Factorial(self,n):
		j=1
		for i in range(1,n+1):
			j=j*i
		return j
	def nPr(self,n,r):
		return self.Factorial(n)/self.Factorial(n-r)
	def nCr(self,n,r):
		return self.nPr(n,r)/self.Factorial(r)
	def AnB(self,A,B):
		C=[]
		for i in range(len(A)):
			for j in range(len(B)):
				if A[i]==B[j]:
					C=C+[B[j]]
		return C 
	def Ac(self,A,S):
		S2=list(S)
		for i in A[:]:
			S2.remove(i)
		return S2
	def AUB(self,A,B):
		C=A+B
		D=self.AnB(A,B)
		for i in D[:]:
			C.remove(i)
		C.sort()
		return C
	def AEB(self,A,B):
		n=0
		for i in A[:]:
			for j in B[:]:
				if i == j:
					n=n+1
		if n == len(A) and len(A)>1:
			return True
		return False
		
	def AcB(self,A,B):
		n=0
		for i in A[:]:
			for j in B[:]:
				if i == j:
					n=n+1
		if n == len(A):
			return True
		return False
	def P(self,A,S):
		if self.AcB(A,S):
			return float(len(A))/float(len(S))
		else:
			return 0
	def P_BlA(self,A,B,S):
		return self.P(self.AnB(A,B),S)/self.P(A,S)
	def nPIr(self,n,r):
		j=1
		for i in range(0,r):
			j=j*i
		return j
	def nHr(self,n,r):
		return self.nCr(n+r-1,r)
	def AmB(self,A,B,S):
		C=self.Ac(B,S)
		return self.AnB(A,C)
