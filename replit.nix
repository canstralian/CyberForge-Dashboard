{pkgs}: {
  deps = [
    pkgs.rustc
    pkgs.libiconv
    pkgs.cargo
    pkgs.postgresql
    pkgs.libxcrypt
    pkgs.libyaml
    pkgs.glibcLocales
  ];
}
