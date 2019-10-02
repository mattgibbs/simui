import numpy as np
"""least_squares.py performs least-squares fitting."""
def fit(Q, s, sig=None):
	renorm = False
	if sig is None:
		sig = 1
		renorm = True
	N, n = np.shape(Q)
	if n==1 or N==1:
		Q = Q[:]
		(N, n) = np.shape(Q)

	if n > N:
		raise ValueError("Not enough data points to fit the curve.")

	try:
		n_sig = len(sig)
	except TypeError:
		n_sig = 1
	if n_sig == 1:
		sig = sig * np.ones((N,1))
	elif n_sig != N:
		raise ValueError("len(sig) must be equal to number of data points.")
	sig2 = np.asarray(sig) ** 2.0
	e = sig2 ** -1
	E = e*np.ones((1,n))
	G = np.mat(np.array(Q)*np.array(E))
	NDF = N - n
	if n == N:
		NDF = 1
	
	V = np.linalg.inv(np.mat(Q).transpose() * G)
	t = V*G.transpose()
	dR = np.sqrt(np.diag(V))
	T = np.mat(Q)*t
	dy2 = np.mat(np.asarray(T)**2)*sig2
	dy = np.sqrt(np.asarray(dy2))
	R = np.mat(t)*np.mat(s)
	y = Q*R
	chi = np.mat((np.mat(s) - np.mat(y))/sig)
	chisq = (chi.transpose()*chi)/NDF

	if renorm:
		chi = np.asarray(np.sqrt(chisq))
		dR = dR*chi
		dy = dy*chi
		V = np.asarray(V)*np.asarray(chisq)
		chisq = 1

	return (y, dy, R, dR, chisq, V)

if __name__ == '__main__':
	#if this file is run directly from the command line it runs a test fit.
	x = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]).transpose()
	Q = np.array([x, np.ones((len(x),1))]).transpose()
	s = np.array([0.0, 1.1, 1.8, 3.3, 3.9, 5.1]).transpose()
	print(fit(Q,s))
