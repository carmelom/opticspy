from __future__ import division as __division__
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from . import cal_tools,trace, wavelength
# All analysis functions

def spotdiagram(Lens, field_plot=None, wave_plot=None, surface_plot=-1, n=12, grid_type='grid', wl_colors=True):
    '''
    Show spotdiagram of image plane for different field
    input:
    Lens: Lens Class
    field_plot: list [1,2,3]
    wave_plot: plot wave list [1,2,3]
    '''
    if field_plot is None: # plot all fields
        field_plot = list(range(1, len(Lens.field_angle_list)+1))
    if wave_plot is None: # plot all wavelengths
        wave_plot = list(range(1, len(Lens.wavelength_list)+1))
    trace.trace_spotdiagram(Lens,n,grid_type)
    field_plot_length = len(field_plot)
    wavelengths = [Lens.wavelength_list[j-1] for j in wave_plot]

    sign_list = ['rs','go','b*','cD','m+','yx','k1','ws']
    marker_list = ['s','o','^','*','D','x','1','s']
    if wl_colors:
        c_list = [wavelength.wavelength_to_rgb(u) for u in wavelengths]
    else:
        #c_list = ['b','g','r','c','m','y','k','w']
        c_list = ['C%d'%i for i in range(len(wave_plot))] # welcome to matplotlib2

    fig, axes = plt.subplots(1, field_plot_length, figsize=(5*field_plot_length, 5), dpi=80, squeeze=False)
    axes = axes.ravel()
    title = '%s spotdiagram'%Lens.lens_name
    fig.canvas.set_window_title(title)
    fig.suptitle(title, fontsize="x-large")
    for p, field_num in enumerate(field_plot):
        label2 = []
        ax = axes[p]
        for m, wave_num in enumerate(wave_plot):
            ax_kwargs = dict(marker=marker_list[m], color=c_list[m])
            fig, ax, wl_label = plot_spotdiagram_field_wave(Lens,field_num,wave_num, surface_num=surface_plot,
                                        ax=ax, annotate=False, **ax_kwargs)
            label2.append(wl_label)


        Relative_field = str(round(Lens.field_angle_list[field_num-1]/Lens.field_angle_list[-1],2))
        str_angle = str(Lens.field_angle_list[field_num-1]) + ' DG'
        label1 = 'Field'+str(field_num)+'\n'+'0.00, '+Relative_field+'\n'+'0.000, '+str_angle
        ax.annotate(label1, xy=(0.08, 0.73), xycoords='axes fraction', fontsize=12)

        ax.annotate('\n'.join(label2), xy=(1.1, 0), xycoords='axes fraction', fontsize=12)

        ax.set_aspect('equal', 'datalim')
        ax.legend(loc='upper left')
    return fig, axes

def spotdiamgram_field_wave(Lens,field_num,wave_num, surface_num=-1):
    if surface_num == -1:
        surface_num = len(Lens.surface_list)
    all_field_ray_dict_list = Lens.field_trace_info
    rays_dict = all_field_ray_dict_list[wave_num-1][field_num-1]
    xy_list = []
    for ray_dict in rays_dict:
        xy_list.append([ray_dict['X'][surface_num-1],ray_dict['Y'][surface_num-1]])
    xy_list = np.asarray(xy_list)
    xy_list = np.transpose(xy_list)
    return xy_list

def plot_spotdiagram_field_wave(Lens,field_num,wave_num, surface_num=-1, ax=None, annotate=True, **kwargs):
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(5, 5), dpi=80,)
    else:
        fig = ax.figure
    xy_list = spotdiamgram_field_wave(Lens,field_num,wave_num, surface_num=surface_num)
    wl = Lens.wavelength_list[wave_num-1]
    ax_kwargs = dict(ls='', marker='o', color=None, mfc='none', label='{:.2f}'.format(wl))
    ax_kwargs.update(kwargs)
    ax.plot(xy_list[0],xy_list[1], **ax_kwargs)
    airy = 1.22 * wl*1e-6 * Lens.FNO
    rms = cal_tools.rms(xy_list)
    r = np.hypot(*xy_list)
    frac_inside = np.count_nonzero(r <= airy)/len(r)
    # c = Circle((xy_list[0].mean(), xy_list[1].mean()), radius=airy, ec=ax_kwargs['color'], fc='none', lw=2)
    c = Circle((xy_list[0].mean(), xy_list[1].mean()), radius=airy, color=ax_kwargs['color'], alpha=0.4, lw=2)
    ax.add_patch(c)
    ax.set_aspect('equal', 'datalim')
    L = max(ax.get_xlim()[1], 1.1*airy)
    ax.set_xlim(-L, L)
    ax.set_ylim(-L, L)
    wl_label = '@{:.2f}\nRMS: {:.5f}\nAiry: {:.5f}\n{:.1f}%\n'.format(wl, rms, airy, frac_inside*100)
    return_args = (fig, ax)
    if annotate:
        ax.annotate(wl_label, xy=(1.1, 0), xycoords='axes fraction', fontsize=12)
    else:
        return_args += (wl_label,)
    return return_args

def Ray_fan(Lens,field_plot,wave_plot):
    '''
    Plot ray fan
    '''
    trace.trace_Y_fan(Lens)
    trace.trace_X_fan(Lens)
    field_plot_length = len(field_plot)
    wave_plot_length = len(wave_plot)
    c_list = ['b','g','r','c','m','y','k','w']
    fig = plt.figure(5,figsize=(10, 9), dpi=80)
    fig.canvas.set_window_title('Ray aberration')
    fig.suptitle("Ray aberration: "+Lens.lens_name, fontsize="x-large")
    m = 0
    Py = np.linspace(-1,1,25)
    Px = np.linspace(0,1,20)
    max_E = 0
    for wave_num in wave_plot:
        n = field_plot_length
        for field_num in field_plot:
            #plot y fan
            plt.subplot(field_plot_length, 2, n*2-1)
            xy_list = Y_fan_field_wave(Lens,field_num,wave_num)
            Ey = xy_list[1]-xy_list[1][12]
            plt.plot(Py,Ey,c=c_list[m])
            max_tmp = max(abs(Ey))
            if max_tmp > max_E:
                max_E = max_tmp
            #plot x fan
            plt.subplot(field_plot_length, 2, n*2)
            xy_list = X_fan_field_wave(Lens,field_num,wave_num)
            Ex = xy_list[0]-xy_list[0][0]
            max_tmp = max(abs(Ex))
            if max_tmp > max_E:
                max_E = max_tmp
            plt.plot(Px,Ex,c=c_list[m])
            n = n - 1
        m = m + 1


    n = field_plot_length
    for field_num in field_plot:
        # Y fan axis
        plt.subplot(field_plot_length, 2, n*2-1)
        ax = plt.gca()
        if n == 1:
            ax.set_title("Tangential", fontsize=16)
        ax.set_xlim([-1.1,1.1])
        ax.set_ylim([-max_E*1.1,max_E*1.1])
        plt.plot([-1,1],[0,0],c='k')
        plt.plot([0,0],[-max_E,max_E],c='k')
        ax.set_ylabel('Field '+str(field_num))
        Relative_field = str(round(Lens.field_angle_list[field_num-1]/Lens.field_angle_list[-1],2))
        str_angle = str(Lens.field_angle_list[field_num-1])+' DG'
        label = Relative_field+' Relative\n'+ 'Field Height\n'+ str_angle

        ax.annotate(label, xy=(0.7, 0.7), xycoords='axes fraction', fontsize=12)
        # X fan axis
        plt.subplot(field_plot_length, 2, n*2)
        ax = plt.gca()
        if n == 1:
            ax.set_title("Sagittal", fontsize=16)
        ax.set_xlim([-0.1,1.1])
        ax.set_ylim([-max_E*1.1,max_E*1.1])
        plt.plot([0,1],[0,0],c='k')
        plt.plot([0,0],[-max_E,max_E],c='k')

        n = n - 1
    plt.show()
    return 0

def Y_fan(Lens,field_plot,wave_plot):
    '''
    Tangential fan,plot Ey vs Py
    '''
    trace.trace_Y_fan(Lens)
    field_plot_length = len(field_plot)
    wave_plot_length = len(wave_plot)

    c_list = ['b','g','r','c','m','y','k','w']
    fig = plt.figure(3,figsize=(5, 9), dpi=80)
    fig.canvas.set_window_title('Ray aberration')
    fig.suptitle("Ray aberration", fontsize="x-large")

    m = 0
    Py = np.linspace(-1,1,25)
    max_Ey = 0
    for wave_num in wave_plot:
        n = field_plot_length
        for field_num in field_plot:
            plt.subplot(field_plot_length, 1, n)
            xy_list = Y_fan_field_wave(Lens,field_num,wave_num)
            Ey = xy_list[1]-xy_list[1][12]
            plt.plot(Py,Ey,c=c_list[m])
            #xy_list[1][12] is the Ey generate by Py=0
            max_tmp = max(abs(Ey))
            if max_tmp > max_Ey:
                max_Ey = max_tmp
            n = n - 1
        m = m + 1


    n = field_plot_length
    for field_num in field_plot:
        plt.subplot(field_plot_length, 1, n)
        ax = plt.gca()
        ax.set_xlim([-1.1,1.1])
        ax.set_ylim([-max_Ey*1.1,max_Ey*1.1])
        plt.plot([-1,1],[0,0],c='k')
        plt.plot([0,0],[-max_Ey,max_Ey],c='k')
        n = n - 1

    plt.show()
    return 0

def Y_fan_field_wave(Lens,field_num,wave_num):
    all_Y_fan_ray_dict_list = Lens.Y_fan_info
    n = len(Lens.surface_list)-1
    rays_dict = all_Y_fan_ray_dict_list[wave_num-1][field_num-1]
    xy_list = []
    for ray_dict in rays_dict:
        xy_list.append([ray_dict['X'][n],ray_dict['Y'][n]])
    xy_list = np.asarray(xy_list)
    xy_list = np.transpose(xy_list)
    return xy_list


def X_fan(Lens,field_plot,wave_plot):
    '''
    Sagittal fan,plot Ex vs Px
    '''
    trace.trace_X_fan(Lens)
    field_plot_length = len(field_plot)
    wave_plot_length = len(wave_plot)

    c_list = ['b','g','r','c','m','y','k','w']
    fig = plt.figure(4,figsize=(5, 9), dpi=80)
    fig.canvas.set_window_title('Ray aberration')
    fig.suptitle("Ray aberration", fontsize="x-large")
    m = 0
    Px = np.linspace(0,1,20)
    max_Ex = 0
    for wave_num in wave_plot:
        n = field_plot_length
        for field_num in field_plot:
            plt.subplot(field_plot_length, 1, n)
            xy_list = X_fan_field_wave(Lens,field_num,wave_num)
            Ex = xy_list[0]-xy_list[0][0]
            max_tmp = max(abs(Ex))
            if max_tmp > max_Ex:
                max_Ex = max_tmp
            plt.plot(Px,Ex,c=c_list[m])
            #xy_list[0][0] is the Ex generate by Px=0
            n = n - 1
        m = m + 1


    n = field_plot_length
    for field_num in field_plot:
        plt.subplot(field_plot_length, 1, n)
        ax = plt.gca()
        ax.set_xlim([-0.1,1.1])
        ax.set_ylim([-max_Ex*1.1,max_Ex*1.1])
        plt.plot([0,1],[0,0],c='k')
        plt.plot([0,0],[-max_Ex,max_Ex],c='k')
        n = n - 1
    plt.show()
    return 0

def X_fan_field_wave(Lens,field_num,wave_num):
    all_X_fan_ray_dict_list = Lens.X_fan_info
    n = len(Lens.surface_list)-1
    rays_dict = all_X_fan_ray_dict_list[wave_num-1][field_num-1]
    xy_list = []
    for ray_dict in rays_dict:
        xy_list.append([ray_dict['X'][n],ray_dict['Y'][n]])
    xy_list = np.asarray(xy_list)
    xy_list = np.transpose(xy_list)
    return xy_list
