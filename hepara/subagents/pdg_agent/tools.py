import pdg
from pdg.errors import PdgAmbiguousValueError, PdgNoDataError
from pdg.particle import PdgParticle
from typing import List

pdg_api = pdg.connect()

COMMON_ALIASES = {
  "gamma": ["photon", "light quantum"],
  "g": ["gluon"],
  "graviton": ["gravity quantum"],
  "W": ["W boson", "charged weak boson"],
  "Z": ["Z boson", "neutral weak boson"],
  "H": ["Higgs", "Higgs boson"],
  "Axions (A0) and Other Very Light Bosons": [
    "axion",
    "axions",
    "A0",
    "very light boson",
  ],
  "e": ["electron", "positron", "electron or positron"],
  "mu": ["muon", "antimuon", "muon or antimuon"],
  "tau": ["tau lepton", "antitau", "tau or antitau"],
  "nu_e": ["electron neutrino", "electron antineutrino"],
  "nu_mu": ["muon neutrino", "muon antineutrino"],
  "nu_tau": ["tau neutrino", "tau antineutrino"],
  "u": ["up", "u quark", "up quark"],
  "d": ["down", "d quark", "down quark"],
  "s": ["strange", "s quark", "strange quark"],
  "c": ["charm", "c quark", "charm quark"],
  "b": ["bottom", "beauty", "b quark", "bottom quark", "beauty quark"],
  "t": ["top", "truth", "t quark", "top quark", "truth quark"],
  "pi+-": ["charged pion", "charged pions", "pion plus or minus"],
  "pi0": ["neutral pion"],
  "eta": ["eta meson"],
  "K+-": ["charged kaon", "charged kaons", "kaon plus or minus"],
  "K0": ["neutral kaon"],
  "K(S)0": ["K short", "K-short", "short-lived neutral kaon"],
  "K(L)0": ["K long", "K-long", "long-lived neutral kaon"],
  "D+-": ["charged D meson", "D meson plus or minus"],
  "D0": ["neutral D meson"],
  "D_s()+-": ["charged D-s meson", "D strange meson"],
  "B+-": ["charged B meson", "B meson plus or minus"],
  "B0": ["neutral B meson"],
  "B_s()0": ["neutral B-s meson", "B strange meson"],
  "B_c()+": ["charged B-c meson", "B charm meson"],
  "J/psi(1S)": ["J/psi", "J psi", "J/psi meson", "charmonium ground state"],
  "Upsilon(1S)": ["Upsilon", "bottomonium ground state"],
  "p": ["proton"],
  "n": ["neutron"],
  "Lambda": ["Lambda baryon"],
  "Sigma+": ["positive Sigma baryon"],
  "Sigma0": ["neutral Sigma baryon"],
  "Sigma-": ["negative Sigma baryon"],
  "Xi0": ["neutral Xi baryon"],
  "Xi-": ["negative Xi baryon"],
  "Omega-": ["negative Omega baryon"],
}

GENERIC_ALIASES = {
  "pi": ["pion", "pions"],
  "K": ["kaon", "kaons"],
  "D": ["D meson", "D mesons"],
  "B": ["B meson", "B mesons"],
}

def _get_all_particle_names() -> List[str]:
    all_data = pdg_api.get_all(data_type_key='PART')
    all_particle_names =[]
    for data in all_data:
        all_particle_names.append(data.description)
    return all_particle_names

def _get_exact_name(name: str) -> str:
    all_exact_names = _get_all_particle_names()
    stripped_name = name.strip()
    normalized_name = stripped_name.casefold()

    for exact_name in all_exact_names:
        if stripped_name == exact_name:
            return exact_name

    for generic_name in GENERIC_ALIASES:
        if stripped_name == generic_name:
            return generic_name

    for exact_name in all_exact_names:
        if normalized_name == exact_name.strip().casefold():
            return exact_name

    for exact_name, aliases in COMMON_ALIASES.items():
        for alias in aliases:
            if normalized_name == alias.strip().casefold():
                return exact_name

    for generic_name, aliases in GENERIC_ALIASES.items():
        normalized_aliases = [alias.strip().casefold() for alias in aliases]
        if (normalized_name == generic_name.casefold()
                or normalized_name in normalized_aliases):
            return generic_name

    return ""

def _get_particle_by_name(name: str) -> PdgParticle | List[PdgParticle] | None:
    lookup_name = name.strip()
    try:
        return pdg_api.get_particle_by_name(lookup_name)
    except PdgAmbiguousValueError:
        return pdg_api.get_particles_by_name(lookup_name)
    except (ValueError, PdgNoDataError):
        exact_name = _get_exact_name(name)
        if not exact_name:
            return None
        try:
            return pdg_api.get_particle_by_name(exact_name)
        except PdgAmbiguousValueError:
            return pdg_api.get_particles_by_name(exact_name)
        except (ValueError, PdgNoDataError):
            return None

def get_particle_masses(name: str) -> str:
    particles = _get_particle_by_name(name)
    if particles is None:
        return f"Particle {name} was not found."

    results = ""
    if isinstance(particles, PdgParticle):
        for mass in particles.masses():
            results += f"{mass.description}: {mass.value} {mass.units}\n"
    elif isinstance(particles, List):
        for particle in particles:
            for mass in particle.masses():
                results += f"{mass.description}: {mass.value} {mass.units}\n"

    return results or f"Particle {name} has no mass data."
