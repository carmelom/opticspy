from . import surface, field, analysis, wavelength, first_order_tools, draw

# Ray Class


class Lens(object):
	# WHY THE FUCK IS THIS A CLASS ATTRIBUTE???
	# surface_list = []

	def __init__(self, lens_name='', creator='', fix_diameter=True):
		self.lens_name = lens_name
		self.creator = creator
		self.surface_list = [] # moved to object attribute
		self.field_angle_list = []
		self.wavelength_list = []
		self._fix_diameter = fix_diameter
		self._FNO = None
		self._EPD = None
		self.tmp_ray = []
		self.object_position = 0
		self.image_plane_ray_list = []
		self.field_trace_info = []
		self.Y_fan_info = []

	@property
	def EFL(self):
		return first_order_tools.EFL(self, 0, 0)

	@property
	def BFL(self):
		return first_order_tools.BFL(self)

	@property
	def OAL(self,):
		return first_order_tools.OAL(self,)

	@property
	def image_position(self):
		return first_order_tools.image_position(self)

	@property
	def EP(self):
		return first_order_tools.EP(self)

	@property
	def EPD(self):
		if self._fix_diameter:
			return self._EPD
		else:
			return self.BFL / self.FNO
	@EPD.setter
	def EPD(self, value):
		if self._fix_diameter:
			self._EPD = value
		else:
			raise AttributeError("can't set attribute")

	@property
	def FNO(self):
		if self._fix_diameter:
			return self.BFL / self.EPD # i should rathere use the "exit" pupil diameter
		else:
			return self._FNO
	@FNO.setter
	def FNO(self, value):
		if self._fix_diameter:
			raise AttributeError("can't set attribute")
		else:
			self._FNO = value

	@property
	def EX(self):
		return first_order_tools.EX(self)

	def lens_info(self):
		print(self.lens_name)
		print(self.creator)

	def list_surface(self):
		print('list all surface information')
		for i in self.surface_list:
			print(i)

	def list_fields(self):
		print('list all fields information')
		for i in self.field_angle_list:
			print('Field angle:', i)

	def refresh_paraxial(self, force_surface0=False, verbose=False):
		if verbose:
			print(f'{self.lens_name} refresh paraxial\n-----------------------')
		if force_surface0 or self.surface_list[0].radius < 1e6:
			# entrance pupil fake surface use as surface 1
			self.surface_list.insert(0, surface.Surface(wavelength_list=self.wavelength_list, number=0,
														radius=1e6, thickness=0, glass='air', STO=False,
														__diameter__=0)
														)
			for S in self.surface_list:
				S.number += 1
		self.object_position = -1000000    # temporary only for infinity conjugate
		self.solve_imageposition()
		start = 2
		end = len(self.surface_list)
		OAL = first_order_tools.OAL(self, start, end)
		Pos_z = OAL * 0.1
		self.surface_list[0].thickness = Pos_z

	def solve_imageposition(self):
		t0 = self.image_position # - self.OAL()
		self.surface_list[-2].thickness = t0
		#print(f'Last surface thickness set to {t0:.2f} mm')

	def first_order(self):
		print('first order information')

	def radius(self, surface_number):
		print('surface radius')

	def __str__(self,):
		text = '\n'.join([f'{self.lens_name} paraxial informations:',
				'---------------------------------------',
				f'Effective focal length    EFL: {self.EFL:.3f} mm',
				f'Entrance pupil diameter   EPD: {self.EPD:.3f} mm',
				f'F-number                  f_#: {self.FNO:.3f}',
				f'Image position             z0: {self.image_position:.3f} mm',
				f'Overall length            OAL: {self.OAL:.2f} mm'])
		return text
# -----------------------surface functions-----------------------
# badly written, it probably adds * to the Lens class itself*
	# def add_surface(self,number,radius,thickness,glass,STO=False,output=False):
	# 	surface.add(self,number,radius,thickness,glass,STO,output)
 	# def update_surface(self,number,radius,thickness,index,STO):
	# 	surface.update(self,number,radius,thickness,index,STO)
	# def delete_surface(self,number,radius,thickness,index,STO):
	# 	surface.delete(self,number,radius,thickness,index,STO)

	def add_surface(self, number=None, radius=1e6, thickness=0, glass='air', STO=False, output=False):
		number = len(self.surface_list)+1 if number is None else number
		S = surface.Surface(wavelength_list=self.wavelength_list, number=number,\
							radius=radius, thickness=thickness, glass=glass, STO=STO,\
							__diameter__=0)
		self.surface_list.append(S)
		surface.print_add_surface(number,radius,thickness,glass,STO,output=output)

	def print_surface_list(self):
		surface.print_surface_list(self)

# -----------------------Field functions--------------------------
	def add_field_YAN(self,angle):
		field.add_field_YAN(self,angle)

# -----------------------Wavelength Fucntions---------------------
	def add_wavelength(self,wl):
		print('Add wavelength '+ str(wl) + ' nm done')
		wavelength.add(self,wl)

	def list_wavelengths(self):
		print('List all wavelength information')
		for i in self.wavelength_list:
			print('Wavelength',i,'nm')

# -----------------------Spotdiagram------------------------------
	def spotdiagram(self):
		analysis.spotdiagram(self)

	def list_image_ray_info(self):
		print(self.image_plane_ray_list)
