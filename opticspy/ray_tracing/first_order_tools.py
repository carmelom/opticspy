# first order tools, find EPD, calculate system power, etc
from __future__ import division as __division__
import numpy as __np__
import matplotlib.pyplot as __plt__

def print_verbose(*args, verbose=False):
	if verbose:
		print(*args)


def start_end(Lens,start_surface=0,end_surface=0, verbose=False):
	'''
	return start end surface index
	'''
	if start_surface == 0:
		start = 2
		end = len(Lens.surface_list) - 1
	else:
		start = start_surface
		end = end_surface
	print_verbose('start surface:',start, verbose=verbose)
	print_verbose('end surface:',end, verbose=verbose)
	return start,end


def T(t,n):
	'''
	T matrix generate
	'''
	return __np__.array([[1,t/n],[0,1]])

def R(c,n_left,n_right):
	'''
	R matrix generate
	'''
	return __np__.array([[1,0],[-c*(n_right-n_left),1]])

def ABCD(matrix_list):
	'''
	ABCD matrix calculator
	input: a matrix list
	output: ABCD matrix
	'''
	M = matrix_list.pop()
	while matrix_list:
		M = __np__.dot(M,matrix_list.pop())
	return M[0,0],M[0,1],M[1,0],M[1,1]

def ABCD_start_end(Lens,start_surface=0,end_surface=0, verbose=False):
	'''
	matrix calculation
	------------------------------------
	input: Lens Class,start_surface,end_surface
	output: ABCD matrix
	'''
	s = Lens.surface_list
	start,end = start_end(Lens,start_surface,end_surface, verbose)
	R_matrix = []
	T_matrix = []
	RT_matrix = []
	for i in range(start,end+1):
		i = i - 1
		# print 'i:',i
		# print 'surface_num',s[i].number
		c = 1/s[i].radius
		# now use central wavelength as reference
		n_left = s[i-1].indexlist[int(len(s[i-1].indexlist)/2)]
		n_right = s[i].indexlist[int(len(s[i].indexlist)/2)]
		t = s[i].thickness
		R1 = R(c,n_left,n_right)
		T1 = T(t,n_right)
		# print R1
		# print T1
		RT_matrix.append(R1)
		if i+1 != end:
			RT_matrix.append(T1)
	# print '--------------------------------'
	# for i in RT_matrix:
	# 	print i
	# print '--------------------------------'
	A,B,C,D = ABCD(RT_matrix)
	return A,B,C,D


def list(Lens):
	'''
	List first order information of a lens system
	input: Lens Class
	output: print information
			refresh Lens first order information
	'''
	return 0


# input should be Lens class and surface number(s1..5)
def EFL(Lens,start_surface,end_surface, verbose=False):
	print_verbose('------------Calculating EFL---------------', verbose=verbose)
	A,B,C,D = ABCD_start_end(Lens,start_surface,end_surface, verbose)
	EFL = -1/C
	print_verbose('Rear Focal Length f\':',-1/C,'\n', verbose=verbose)
	return EFL

def BFL(Lens, verbose=False):
	BFL = Lens.surface_list[-2].thickness
	print_verbose('------------Calculating BFL---------------', verbose=verbose)
	print_verbose('Back focal length:',BFL,'\n', verbose=verbose)
	return BFL

def FFL():
	return 0

def OAL(Lens, start_surface=0, end_surface=0, verbose=False):
	s = Lens.surface_list
	start,end = start_end(Lens,start_surface,end_surface, verbose)
	OAL = 0
	for i in range(start,end):
		OAL = OAL + s[i-1].thickness
	print_verbose('------------Calculating OAL---------------', verbose=verbose)
	print_verbose('Overall length:',OAL,'\n', verbose=verbose)
	return OAL

def image_position(Lens, verbose=False):
	'''
	Calculate paraxial image position
	'''
	print_verbose('------------Calculating image position---------------', verbose=verbose)
	s = Lens.surface_list
	z = Lens.object_position  # object distance
	if verbose:
		print_verbose('object distance',z, verbose=verbose)
	A,B,C,D = ABCD_start_end(Lens,start_surface=0,end_surface=0, verbose=verbose)
	f = -1/C
	fp = -1/C
	Fp = -A/C
	zp = f*fp/z
	# image_position = Fp + zp
	image_position = -A/C + 1/(z + D/C)/C**2
	print_verbose('image position:',image_position,'\n', verbose=verbose)
	return image_position

def EP(Lens, verbose=False):
	# Entrance pupil's position and diameter
	print_verbose('---------Calculating Entrance Pupil Position-----------', verbose)
	s = Lens.surface_list

	for surface in s:
		if surface.STO == True:
			n = surface.number
			print_verbose('STOP Surface',n, verbose=verbose)
			if n == 2:
				EP = 0
				return EP
			else:
				t_stop = s[n-2].thickness
				print_verbose('STOP thickness',t_stop, verbose=verbose)
				start_surface = 2
				end_surface = n - 1
		else:
			pass
	A,B,C,D = ABCD_start_end(Lens,start_surface,end_surface, verbose)
	phi = -C
	P = (D-1)/C
	Pp = (1-A)/C
	lp = t_stop-Pp
	l = 1/(1/lp - phi)
	EP = l + P
	print_verbose('entrance pupil position EP:',EP,'\n', verbose=verbose)
	return EP

def EX(Lens, verbose=False):
	# Exit pupil's position and diameter
	print_verbose('---------Calculating Exit Pupil Position-----------', verbose=verbose)
	s = Lens.surface_list
	for surface in s:
		if surface.STO == True:
			n = surface.number
			print_verbose('STOP Surface',n, verbose=verbose)
			if n == len(s)-1:
				EX = 0   # if stop at last, EX = 0, code V do this
				print_verbose('exit pupil position EX:',EX,'\n', verbose=verbose)
				return EX
			else:
				t_stop = s[n-1].thickness
				print_verbose('STOP thickness',t_stop, verbose=verbose)
				start_surface = n + 1
				end_surface = len(s) - 1
		else:
			pass
	A,B,C,D = ABCD_start_end(Lens,start_surface,end_surface, verbose)
	phi = -C
	P = (D-1)/C
	Pp = (1-A)/C
	l = -(t_stop+P)
	lp = 1/(1/l + phi)
	EX = lp + Pp
	print_verbose('exit pupil position EX:',EX,'\n', verbose=verbose)
	return EX

## note for future work: for system no in air, need to change part of program,
## For example, 'Rear Focal Length f\':',-1/C ----> -np/C, etc
