# Install and configure the Flask Api Skeleton
class deed_api (
    $port = '9020',
    $host = '0.0.0.0',
    $source = 'https://192.168.249.38/digital-mortgage/deed-api',
    $branch_or_revision = 'develop',
    $subdomain = 'deedapi',
    $domain = undef,
    $owner = 'vagrant',
    $group = 'vagrant',
    $app_dir = "/opt/${module_name}",
) {
  require ::standard_env

  vcsrepo { "${app_dir}":
    ensure   => latest,
    provider => git,
    source   => $source,
    revision => $branch_or_revision,
    owner    => $owner,
    group    => $group,
    notify   => Service[$module_name],
  }

  file { "${app_dir}/bin/run.sh":
    ensure  => 'file',
    mode    => '0755',
    owner   => $owner,
    group   => $group,
    content => template("${module_name}/run.sh.erb"),
    require => Vcsrepo["/opt/${module_name}"],
    notify  => Service[$module_name],
  }

  file { "${app_dir}/bin/app_requirements.sh":
    ensure  => 'file',
    mode    => '0755',
    owner   => $owner,
    group   => $group,
    content => template("${module_name}/app_requirements.sh.erb"),
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
    notify  => [
      Exec['systemctl-daemon-reload'],
      Service[$module_name]
    ],
  }

  exec {"${app_dir}/bin/app_requirements.sh":
    cwd       => "${app_dir}",
    user      => $owner,
    logoutput => true,
    environment => ["DEED_DATABASE_NAME=deed_api","ESEC_CLIENT_URI=http://127.0.0.1:9040"],
    require   => [
      Vcsrepo["${app_dir}"],
      Standard_env::Db::Postgres[$module_name],
      File["${app_dir}/bin/app_requirements.sh"],
    ],
  }

  service { $module_name:
    ensure   => 'running',
    enable   => true,
    provider => 'systemd',
    require  => [
      Vcsrepo["${app_dir}"],
      File["/opt/${module_name}/bin/run.sh"],
      File["/etc/systemd/system/${module_name}.service"],
      File["/var/run/${module_name}"],
      Standard_env::Db::Postgres[$module_name],
      Exec["${app_dir}/bin/app_requirements.sh"],
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
