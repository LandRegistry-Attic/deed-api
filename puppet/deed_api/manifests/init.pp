# Install and configure the Flask Api Skeleton
class deed_api (
    $port = '9020',
    $host = '0.0.0.0',
    $source = 'https://github.com/LandRegistry/dm-deed-api',
    $branch_or_revision = 'master',
    $subdomain = 'deedapi',
    $domain = undef,
    $owner = 'vagrant',
    $group = 'vagrant'
) {
  require ::standard_env

  vcsrepo { "/opt/${module_name}":
    ensure   => latest,
    provider => git,
    source   => $source,
    revision => $branch_or_revision,
    owner    => $owner,
    group    => $group,
    notify   => Service[$module_name],
  }

  file { "/opt/${module_name}/bin/run.sh":
    ensure  => 'file',
    mode    => '0755',
    owner   => $owner,
    group   => $group,
    content => template("${module_name}/run.sh.erb"),
    require => Vcsrepo["/opt/${module_name}"],
    notify  => Service[$module_name],
  }

  file { "/var/run/${module_name}":
    ensure => 'directory',
    owner  => $owner,
    group  => $group,
  }

  file { "/etc/systemd/system/${module_name}.service":
    ensure  => 'file',
    mode    => '0755',
    owner   => $owner,
    group   => $group,
    content => template("${module_name}/service.systemd.erb"),
    notify  => [Exec['systemctl-daemon-reload'], Service[$module_name]],
  }
  service { $module_name:
    ensure   => 'running',
    enable   => true,
    provider => 'systemd',
    require  => [
      Vcsrepo["/opt/${module_name}"],
      File["/opt/${module_name}/bin/run.sh"],
      File["/etc/systemd/system/${module_name}.service"],
      File["/var/run/${module_name}"],
      Standard_env::Db::Postgres[$module_name],
    ],
  }

  file { "/etc/nginx/conf.d/${module_name}.conf":
    ensure  => 'file',
    mode    => '0755',
    content => template("${module_name}/nginx.conf.erb"),
    owner   => $owner,
    group   => $group,
    notify  => Service['nginx'],
  }

  standard_env::db::postgres { $module_name:
   user     => $owner,
   password => $owner,
 }

  if $environment == 'development' {
    standard_env::dev_host { $subdomain: }
  }

}
