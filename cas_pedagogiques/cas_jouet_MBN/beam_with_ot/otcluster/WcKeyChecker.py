"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin

Checks a wckey for sbatch.
"""

from subprocess import Popen, PIPE


class WcKeyChecker:
    def __init__(
        self,
        program="cce_wckeys",
        option_project="--projects",
        option_code="--codes",
        initialize_from_list=True,
    ):
        """
        Check a wckey

        Parameters
        ----------
        program : str
            The wckeys program
        option_project : str
            The option of the wckeys program which prints the list of
            known project names.
        option_code : str
            The option of the wckeys program which prints the list of
            known code names.
        initialize_from_list : bool
            Set to True to initialize from a built-in list of names.
            Otherwise, use the program to build the list (this is longer).
        """
        self.program = program
        self.option_project = option_project
        self.option_code = option_code
        self.initialized = False
        self.initialize_from_list = initialize_from_list
        self._init()

    def _initFromProgram(self):
        """
        Initialize the list of valid project and code names from the wckeys program.
        """
        if self.initialized:
            return
        # Init valid project names
        process = Popen([self.program, self.option_project], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()
        valid_project_names = output.splitlines()
        self.valid_project_names = [name.decode() for name in valid_project_names]
        # Init valid code names
        process = Popen([self.program, self.option_code], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()
        valid_code_names = output.splitlines()
        self.valid_code_names = [name.decode() for name in valid_code_names]
        # Set the flag
        self.initialized = True

    def _init(self):
        """
        Initialize the list of valid project and code names.
        """
        if self.initialize_from_list:
            self._initFromList()
        else:
            self._initFromProgram()

    def _initFromList(self):
        """
        Initialize the list of valid project and code names from built-in lists.
        """
        if self.initialized:
            return
        # Init valid project names
        self.valid_project_names = [
            "a10cs",
            "a10d2",
            "a10d5",
            "a12ay",
            "a12ff",
            "a12h8",
            "a12jb",
            "a12n7",
            "a12qv",
            "a12vw",
            "arabelle",
            "bil100",
            "chenal3d",
            "cih_dt-hy",
            "cspit",
            "doaat",
            "dsp",
            "dteam",
            "dtglabdata",
            "dtsi",
            "ehmouvhy",
            "forcity",
            "formation",
            "hpcwe",
            "ird",
            "lamsid",
            "lhsv",
            "p10kq",
            "p10wb",
            "p1139",
            "p1187",
            "p11ie",
            "p11is",
            "p11la",
            "p11lg",
            "p11lp",
            "p11lt",
            "p11mh",
            "p11xk",
            "p11xl",
            "p11xn",
            "p11y5",
            "p11y6",
            "p11y7",
            "p11yb",
            "p11yh",
            "p11yi",
            "p11ym",
            "p1209",
            "p120f",
            "p120i",
            "p120j",
            "p120k",
            "p120r",
            "p120t",
            "p1210",
            "p1218",
            "p121b",
            "p121c",
            "p121j",
            "p121k",
            "p121q",
            "p121w",
            "p123k",
            "p123q",
            "p123s",
            "p123t",
            "p123x",
            "p123z",
            "p1248",
            "p124a",
            "p124c",
            "p124e",
            "p124u",
            "p124y",
            "p1252",
            "p1254",
            "p1256",
            "p1259",
            "p125b",
            "p125c",
            "p125d",
            "p125e",
            "p125h",
            "p125k",
            "p125v",
            "p125w",
            "p1263",
            "p126z",
            "p1273",
            "p1274",
            "p1278",
            "p1279",
            "p127c",
            "p127l",
            "p127m",
            "p127s",
            "p127w",
            "p127y",
            "p127z",
            "p1283",
            "p1284",
            "p1286",
            "p128b",
            "p128c",
            "p128e",
            "p128t",
            "p1290",
            "p129i",
            "p129n",
            "p129r",
            "p129t",
            "p12a4",
            "p12a5",
            "p12a9",
            "p12ab",
            "p12ad",
            "p12ae",
            "p12aj",
            "p12aq",
            "p12ar",
            "p12ax",
            "p12b3",
            "p12b6",
            "p12b8",
            "p12b9",
            "p12bc",
            "p12bd",
            "p12bh",
            "p12bi",
            "p12bs",
            "p12bt",
            "p12bu",
            "p12by",
            "p12bz",
            "p12c0",
            "p12c3",
            "p12c5",
            "p12c6",
            "parc",
            "repli-dt",
            "s167",
            "sime",
            "uk1080",
            "ukarsi",
        ]
        # Init valid code names
        self.valid_code_names = [
            "a3d-cnd",
            "abinit",
            "albert",
            "alm",
            "alphazero",
            "andalosie",
            "ansys",
            "apache",
            "apogee",
            "apogee_jo-hebdo",
            "apogene",
            "apollo2",
            "apollo3",
            "argos",
            "armide",
            "aster",
            "athena_2d",
            "athena_3d",
            "avido",
            "benchmarks",
            "bigdft",
            "btm",
            "c3adao",
            "c3d-cnd",
            "c3ipg",
            "caiman",
            "camelia",
            "carabas",
            "carbones",
            "carmel_3d",
            "catalyst_paraview",
            "cathare",
            "chemsimul",
            "cho",
            "ciwap2",
            "cocagne",
            "code_saturne",
            "colt",
            "comsol",
            "continental",
            "craft",
            "crescendo",
            "crystal",
            "crystal9",
            "cuve1d",
            "cynergie",
            "daccosim",
            "daia",
            "dakota",
            "darwin",
            "datascience",
            "datatech_hpc",
            "deeplan",
            "delwaq",
            "devco",
            "diego",
            "domingo",
            "dragon",
            "dymoka",
            "eaop",
            "eaudyssee",
            "eflow",
            "elsa",
            "emed3",
            "emr-engine",
            "eol",
            "eranos",
            "estipose",
            "europlexus",
            "fds",
            "fdvgrid2",
            "fenix",
            "flow3d",
            "formation",
            "freefem",
            "gab",
            "gab_v2",
            "gama",
            "giroscop",
            "gmsh",
            "goemor",
            "goesto",
            "gpu_sph",
            "hpcc",
            "hpcstats",
            "incompac_3d",
            "interpol",
            "iron",
            "itemiscreate",
            "jrd_elec",
            "jrd_gc",
            "jrd_mcp",
            "jrd_meca",
            "jrd_n4",
            "lakimoca",
            "leon",
            "leonard",
            "leonard2d",
            "leonard3d",
            "local_global",
            "maap4",
            "macao2",
            "magpie",
            "map",
            "maquette3d",
            "mariva",
            "marketlab",
            "mars",
            "maryam",
            "maryam_dipde",
            "mcnp",
            "mcnp_mcnpx",
            "melxor",
            "micromd",
            "ml",
            "moderato",
            "modflow",
            "mordor",
            "morgane",
            "morganium",
            "morphhom",
            "movido",
            "neo",
            "neptune_cfd",
            "numerical_wave_tank",
            "oasys",
            "odyssee",
            "ondes",
            "openfoam",
            "openturns",
            "opus",
            "opusrep",
            "outil_prev_erdf",
            "outils_specifiques_mire",
            "paraview",
            "parc",
            "paris",
            "pe_fortran",
            "petsc",
            "pink",
            "plan4res",
            "pogues",
            "polyphemus",
            "power2",
            "pwscf",
            "pycatshoo",
            "python",
            "quantum",
            "quantum_espresso",
            "r",
            "reef",
            "rme",
            "s3e",
            "safari",
            "salome",
            "salome-meca",
            "sas-sfr",
            "sgdl",
            "sim-diasca",
            "simmer",
            "sims",
            "simulateur_couverture",
            "smack",
            "smartreno",
            "sn_2d1d_micado",
            "snocomb",
            "snowcap",
            "sodata",
            "solfec",
            "soprano",
            "sph_flow",
            "sphflow",
            "ssd",
            "stopt",
            "strapontin",
            "syrthes",
            "telemac_system",
            "temsi-fd",
            "thyc",
            "ticktack",
            "tilt",
            "tripoli",
            "tripoli-4",
            "turing",
            "undefined",
            "varinia",
            "vasp",
            "workbench",
            "wrf",
            "xseismic",
            "yams",
        ]
        # Set the flag
        self.initialized = True

    def check(self, wckey):
        """
        Checks if a wckey is valid.

        Generates an exception otherwise.

        Parameters
        ----------
        wckey : str
            The wckey, in "PROJECT:CODE" format.

        Returns
        ----------
        project : str
            The project name.
        code : str
            The code name.

        Example
        -------
        >>> checker = WcKeyChecker()
        >>> print(checker)
        >>> project, code = checker.check("p125v:openturns")
        """
        # Convert to lower case
        wckey = wckey.lower()
        # Split
        separator = wckey.find(":")
        # TODO: what if there is no ":"?
        # TODO: use the split() method. separator = wckey.split(":") Compute the length of the output value.
        if separator == -1:
            raise ValueError(
                f"The wckey must have format PROJECT:CODE" f"but wckey = {wckey}."
            )
        project = wckey[:separator]
        code = wckey[1 + separator :]
        # Check project name
        is_project_known = project in self.valid_project_names
        if not is_project_known:
            raise ValueError(
                f'Project name "{project}" is unknown. '
                f"Available project names are {self.valid_project_names}."
            )
        # Check code name
        is_code_known = code in self.valid_code_names
        if not is_code_known:
            raise ValueError(
                f'Code name "{code}" is unknown. '
                f"Available code names are {self.valid_code_names}."
            )
        return project, code

    def __str__(self):
        """
        Convert the object into a string.

        This method is typically called with the "print" statement.

        Parameters
        ----------
        None.

        Returns
        -------
        s: str
            The string corresponding to the object.
        """
        s = ""
        s += f"program = {self.program}\n"
        s += f"option_project = {self.option_project}\n"
        s += f"option_code = {self.option_code}\n"
        s += f"valid_project_names = {self.valid_project_names}\n"
        s += f"valid_code_names = {self.valid_code_names}\n"
        return s


if __name__ == "__main__":
    checker = WcKeyChecker()
    print(checker)
    project, code = checker.check("p125v:openturns")
    print(f"project = {project}")
    print(f"code = {code}")
