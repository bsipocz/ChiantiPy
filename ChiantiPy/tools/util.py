"""
Utility functions, many for reading the CHIANTI database files.

Notes
-----
Some of these functions can be replaced by roman numeral and periodic table lookup libraries.
"""

import os, fnmatch
#from types import *
#try:
#    # for Python 3 import
#    import configparser
#except ImportError:
#    # for Python 2 import
#    import ConfigParser as configparser
##from ConfigParser import *
import pickle
from datetime import date

import numpy as np
from scipy import interpolate

import ChiantiPy.tools.constants as const


def between(array,limits):
    """
    Find the indices of `array` corresponding to values in the range given by `limits`

    Parameters
    ----------
    array : `~numpy.ndarray`
    limits : `list` or `tuple` of length 2
    """
    array=np.asarray(array)
    nlines=len(array)
#    hi=np.where(array >= limits[0],range(1,nlines+1),0)
#    lo=np.where(array <= limits[1],range(1,nlines+1),0)
    hi=np.where(array >= limits[0],list(range(1,nlines+1)),0)
    lo=np.where(array <= limits[1],list(range(1,nlines+1)),0)

    hilo=hi&lo
    out=[a -1  for a in hilo if a > 0]
    return out


def z2element(z):
    """
    Convert atomic number `z` to its elemental symbol.
    """
    if z-1 < len(const.El):
        thisel=const.El[z-1]
    else:
        thisel=''
    return thisel


def spectroscopic2name(el,roman):
    """
    Convert from spectroscopic notation, e.g. Fe XI to 'fe_11'

    Parameters
    ----------
    el : `str`
        Elemental symbol, e.g. Fe for iron
    roman : `str`
        Roman numeral spectroscopic symbol
    """
    elu = el.lower()
    romanu = roman.upper()
    idx =const.Ionstage.index(romanu)
    gname = elu+'_'+str(idx+1)
    return gname


def zion2name(z,ion, dielectronic=False):
    """
    Convert atomic number and ion number to generic name, e.g. (26,13) to 'fe_13'

    Parameters
    ----------
    z : `int`
    ion : `int`
    dielectronic : `bool`, optional
    """
    if ion == 0:
        thisone = 0
    elif ion == z+2:
        thisone = 0
    elif (z-1 < len(const.El)) and (ion <= z+1):
        thisone=const.El[z-1]+'_'+str(ion)
        if dielectronic:
            thisone+='d'
    else:
        # this should not actually happen
        thisone = 0
    return thisone


def zion2dir(z,ion, dielectronic=False, xuvtop=''):
    """
    Convert atomic number and ion number to CHIANTI database directory.

    Parameters
    ----------
    z : `int`
    ion : `int`
    dielectronic : `bool`, optional
    xuvtop : `str`, optional
        Set different CHIANTI database than the default
    """
    if xuvtop:
        dir = xuvtop
    else:
        dir=os.environ["XUVTOP"]
    if (z-1 < len(const.El)) and (ion <= z+1):
        thisel=const.El[z-1]
    else:
        thisel=''
    if z-1 < len(const.El):
        thisone=const.El[z-1]+'_'+str(ion)
        if dielectronic:
            thisone+='d'
    else:
        thisone=''
    if thisel != '' :
        fname=os.path.join(dir,thisel,thisone)
    return fname


def zion2filename(z,ion, dielectronic=False, xuvtop=''):
    """
    Convert atomic number and ion number to CHIANTI database filename.

    Parameters
    ----------
    z : `int`
    ion : `int`
    dielectronic : `bool`, optional
    xuvtop : `str`, optional
        Set different CHIANTI database than the default
    """
    if xuvtop:
        dir = xuvtop
    else:
        dir=os.environ["XUVTOP"]
    if (z-1 < len(const.El)) and (ion <= z+1):
        thisel=const.El[z-1]
    else:
        thisel=''
    if z-1 < len(const.El):
        thisone=const.El[z-1]+'_'+str(ion)
        if dielectronic:
            thisone+='d'
    else:
        thisone=''
    if thisel != '' :
        fname=os.path.join(dir,thisel,thisone,thisone)
    return fname


def zion2localFilename(z,ion, dielectronic=False):
    """
    Convert atomic number and ion number to generic file name with current directory at top.

    Parameters
    ----------
    z : `int`
    ion : `int`
    dielectronic : `bool`, optional
    """
    dir='.'
    if (z-1 < len(const.El)) and (ion <= z+1):
        thisel=const.El[z-1]
    else:
        thisel=''
    if z-1 < len(const.El):
        thisone=const.El[z-1]+'_'+str(ion)
        if dielectronic:
            thisone+='d'
    else:
        thisone=''
    if thisel != '' :
        fname=os.path.join(dir,thisel,thisone,thisone)
    return fname


def zion2spectroscopic(z,ion, dielectronic=False):
    """
    Convert atomic number and ion number to spectroscopic notation string

    Parameters
    ----------
    z : `int`
    ion : `int`
    dielectronic : `bool`, optional
    """
    if (z-1 < len(const.El)) and (ion <= z+1):
        spect=const.El[z-1].capitalize()+' '+const.Ionstage[ion-1]
        if dielectronic:
            spect+=' d'
    else:  spect = ''
    return spect


def convertName(name):
    """
    Convert ion name string (e.g. 'fe_13') to atomic number and ion number

    Parameters
    ----------
    name : `str`

    Returns
    -------
    {'Z', 'Ion', 'Dielectronic', 'Element', 'higher', 'lower'} : `dict`
        `higher` and `lower` are the Chianti-style names for the higher and lower ionization stages, respectively.
    """
    s2=name.split('_')
    els=s2[0].strip()
    Z = int(const.El.index(els)+1)
    ions = s2[1].strip()
    d=ions.find('d')
    if d >0 :
        dielectronic=True
        ions = ions.replace('d','')
    else:
        dielectronic=False
    stage = int(ions)
    higher = zion2name(Z, stage+1)
    lower = zion2name(Z, stage-1)
    filename = zion2filename(Z, stage, dielectronic = dielectronic)
    return {'Z':Z,'Ion':stage,'Dielectronic':dielectronic, 'Element':els, 'higher':higher, 'lower':lower, 'filename':filename}


def ion2filename(ions):
    """
    Convert ion name string to generic directory-file name.
    """
    dir=os.environ["XUVTOP"]
    zion=convertName(ions)
    el=z2element(zion['Z'])
    fname=os.path.join(dir,el,ions,ions)
    return fname


def el2z(els):
    """
    Convert elemental symbol to atomic number
    """
    z=const.El.index(els.lower())+1
    return z


def qrp(z,u):
    """
    Calculate :math:`Q_R^{\prime}(Z,u)`, where :math:`u=\epsilon/I` is the impact electron energy in threshold units, from Eq. 2.12 of [1]_.

    Parameters
    ----------
    z : `int`
        Atomic number
    u : array-like
        Impact electron energy in threshold units.

    Returns
    -------
    q : array-like
        1s ionization cross-section, :math:`Q_R^{\prime}(Z,u)`

    Notes
    -----
    Used for calculations of direct ionization cross-sections of the H and He sequences in `ChiantiPy.tools.io.twophotonHRead` and `ChiantiPy.tools.io.twophotonHeRead`, respectively.

    References
    ----------
    .. [1] Fontes, C. et al., 1999, PhRvA, `59, 1329 <http://adsabs.harvard.edu/abs/1999PhRvA..59.1329F>`_
    """
    #
    aa=1.13  # aa stands for A in equ 2.12
    #
    if z >= 16 :
        # use Fontes Z=20, N=1 parameters
        dd=3.70590
        c=-0.28394
        d=1.95270
        cc=0.20594
    else:
    # use Fontes Z=10, N=2 parameters
        dd=3.82652
        c=-0.80414
        d=2.32431
        cc=0.14424
    #
    if z > 20:
        cc+=((z-20.)/50.5)**1.11
    #
    bu=u <= 1.
    q=np.ma.array(u, 'Float64', mask=bu, fill_value=0.)
    #
    #
    q=(aa*np.ma.log(u) + dd*(1.-1./u)**2 + cc*u*(1.-1./u)**4 + (c/u+d/u**2)*(1.-1/u))/u
    #
    q.set_fill_value(0.)  # I don't know why this is necessary
    return q  #  .set_fill_value(0.)


def splomDescale(splom, energy):
    """
    Calculate the collision strength for excitation-autoionization as a function of energy.

    Parameters
    ----------
    energy : array-like
        In eV
    splom : `dict`
        Structure returned by `ChiantiPy.tools.io.splomRead`

    Returns
    -------
    omega : array-like
        Collision strength
    """
    #
    #
    nenergy=energy.size
    nsplom=len(splom['deryd'])
    # for these files, there are 5 spline points
    nspl = 5
    if nenergy > 1:
        omega = np.zeros((nsplom,nenergy),"float64")
    else:
        omega = np.zeros(nsplom,"float64")
    #
    dx = 1./(float(nspl)-1.)
    sxint = dx*np.arange(nspl)  # IDL sx
    for isplom in range(0,nsplom):
        #
        sx1 = energy/(splom['deryd'][isplom]*const.ryd2Ev)  # IDL x_int
        print(' %5i  %12.2e %12.2e'%(isplom, splom['deryd'][isplom], splom['deryd'][isplom]*const.ryd2Ev))
        good = sx1 >= 1.
        # make sure there are some valid energies above the threshold
        if good.sum():
            nbad = nenergy - good.sum()
            c_curr = splom['c'][isplom]
            #
            if splom['ttype'][isplom] == 1:
                sx = 1. - np.log(c_curr)/np.log(sx1[good] - 1. + c_curr)  # IDL sx_int
                y2 = interpolate.splrep(sxint,splom['splom'][:, isplom],s=0)  #allow smoothing,s=0)
                som = interpolate.splev(sx,y2,der=0)
                omega[isplom, nbad:] = som*np.log(sx1[good] -1. + np.exp(1.))
            #
            elif splom['ttype'][isplom] == 2:
                sx =(sx1[good] - 1.)/(sx1[good] -1. + c_curr)
                y2 = interpolate.splrep(sxint,splom['splom'][:, isplom],s=0)  #allow smoothing,s=0)
                som=interpolate.splev(sx,y2,der=0)
                omega[isplom, nbad:] = som
            #
            elif splom['ttype'][isplom] == 3:
                sx = (sx1[good] - 1.)/(sx1[good] -1. + c_curr)
                y2 = interpolate.splrep(sxint,splom['splom'][:, isplom],s=0)  #allow smoothing,s=0)
                som = interpolate.splev(sx,y2,der=0)
                omega[isplom, nbad:] = som/sx1[good]**2
            #
            elif splom['ttype'][isplom] == 4:
                sx = 1. - np.log(c_curr)/np.log(sx1[good] -1. + c_curr)
                y2 = interpolate.splrep(sxint,splom['splom'][:, isplom],s=0)  #allow smoothing,s=0)
                som=interpolate.splev(sx,y2,der=0)
                omega[isplom, nbad:] = som*np.log(sx1[good] -1. + c_curr)
            #
            #
            #
            elif splom['ttype'] > 4:
                print((' splom t_type ne 1,2,3,4 = %4i %4i %4i'%(splom['ttype'],splom['l1'],splom['l2'])))
        else:
            # there are no energies above the threshold
            pass
    #
    #
    omega=np.where(omega > 0.,omega,0.)
    #
    return omega


def dilute(radius):
    """
    Calculate the dilution factor.

    Parameters
    ----------
    radius : array-like
        Distance from the center of a star in units of the stellar radius.

    Notes
    -----
    If `radius` is less than 1.0, returns 0.
    """
    if radius >= 1.:
        d = 0.5*(1. - np.sqrt(1. - 1./radius**2))
    else:
        d = 0.
    return d


def listFiles(path):
    """
    Walks the path and subdirectories to return a list of files.

    Notes
    -----
    This can be replaced by functions in `os.path`.
    """
    alist=os.walk(path)
#    print(' getting file list')
    listname=[]
    for (dirpath,dirnames,filenames) in alist:
        if len(dirnames) == 0:
            for f in filenames:
                file=os.path.join(dirpath,f)
                if os.path.isfile(file):
                    listname.append(file)
        else:
            for f in filenames:
                file=os.path.join(dirpath,f)
                if os.path.isfile(file):
                    listname.append(file)
    return listname


def scale_bti(evin,crossin,f,ev1):
    """
    Apply ionization scaling of [1]_,[2]_ to energy and cross-section.

    Parameters
    ----------
    evin : array-like
        Energy - same units as ev1
    crossin : array-like
        Cross-section
    f : float -  the bt scale factor
    ev1 : array-like (usually in eV)

    Returns
    -------
    [bte,btx] : `list`
        Scaled energy and cross-section

    Notes
    -----
    This is the scaling used in the Dere (2007) calculation of cross sections.  It was derived from
    similar scalings derived in reference [1]

    See Also
    --------
    descale_bti : Descale ionization energy and cross-section

    References
    ----------
    .. [1] Burgess, A. and Tully, J. A., 1992, A&A, `254, 436 <http://adsabs.harvard.edu/abs/1992A%26A...254..436B>`_
    .. [2] Dere, K. P., 2007, A&A, 466, 771, '<http://adsabs.harvard.edu/abs/2007A%26A...466..771D>'
    """
    u = evin/ev1
    bte = 1.-np.log(f)/np.log(u-1.+f)
    btx = u*crossin*(ev1**2)/(np.log(u)+1.)
    return [bte,btx]


def descale_bti(bte,btx,f,ev1):
    """
    Apply ionization descaling of [1]_ to energy and cross-section.

    Parameters
    ----------
    bte : array-like
        Scaled energy
    btx : array-like
        Scaled cross-section
    f : array-like
    ev1 : array-like

    Returns
    -------
    [energy,cross] : `list`
        Descaled energy and cross-section

    Notes
    -----
    Need more details here. Not clear which equations are being used.

    See Also
    --------
    scale_bti : Apply ionization scaling for energy and cross-section

    References
    ----------
    .. [1] Burgess, A. and Tully, J. A., 1992, A&A, `254, 436 <http://adsabs.harvard.edu/abs/1992A%26A...254..436B>`_
    """
    u = 1.-f + np.exp(np.log(f)/(1. - bte))
    energy = u*ev1
    cross = (np.log(u)+1.)*btx/(u*ev1**2)
    return [energy,cross]


def descale_bt(bte,btomega,f,ev1):
    """
    Apply excitation descaling of [1]_ to energy and collision strength

    Parameters
    ----------
    bte : array-like
        Scaled energy
    btomega : array-like
        Scaled collision strength
    f : array-like
    ev1 : array-like

    Returns
    -------
    [energy,omega] : `list`
        Descaled energy and collision strength

    Notes
    -----
    Need more details here. Not clear which equations are being used.

    See Also
    --------
    scale_bt : Apply scaling to excitation energy and cross-section

    References
    ----------
    .. [1] Burgess, A. and Tully, J. A., 1992, A&A, `254, 436 <http://adsabs.harvard.edu/abs/1992A%26A...254..436B>`_
    """
    u=1.-f+np.exp(np.log(f)/(1.-bte))
    energy=u*ev1
    omega=(np.log(u)-1.+np.exp(1.))*btomega
    return [energy,omega]


def scale_bt(evin,omega,f,ev1):
    """
    Apply excitation scaling of [1]_ to energy and collision strength.

    Parameters
    ----------
    evin : array-like
    omega : array-like
    f : array-like
    ev1 : array-like

    Returns
    -------
    [bte,btomega] : `list`
        Scaled energy and collision strength

    Notes
    -----
    Need more details here. Not clear which equations are being used.

    See Also
    --------
    descale_bt : Descale excitation energy and cross-section

    References
    ----------
    .. [1] Burgess, A. and Tully, J. A., 1992, A&A, `254, 436 <http://adsabs.harvard.edu/abs/1992A%26A...254..436B>`_
    """
    u=evin/ev1
    bte=1.-np.log(f)/np.log(u-1.+f)
    btomega=omega/(np.log(u)-1.+np.exp(1.))
    return [bte,btomega]
