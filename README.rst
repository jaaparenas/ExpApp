ExpAPP
=====

Es un proyecto de propósito general diseñado para poder construir fácilmente
cualquier solución basada en una API RESTFull contando ya con funcionalidades
básicas y necesarias relacionadas con autenticación basada en JWT, control
de roles, seguridad, manejo de archivos y otras características comunes que
siempre están presentes en la creación de una API. Partiendo de este principio,
se considera que no debe ser necesario tener que hacer siempre lo mismo, sino
por el contrario poder orientar todo el esfuerzo en abordar de inmediato las
necesidades propias del cada solución.


Este proyecto utiliza el Mini Framework Flask para la creación del Backend al
cual se podra acceder mediente cualquier solución Frontend. En primera instancia
se propone una solución sencilla basada en Nuxt sin embargo se espera que otros
aportes puede generar frontends en otras técnologias tales como React, Angular
entre otros.


Instalación
----------

Para instalar el proyecto a nivel Backend será necesario clonarlo:

.. code-block:: text

    git@github.com:jaaparenas/ExpAPP.git

Una vez clonado será necesario ingresar a la carpeta "backend" e instalar todas
las librerias necesarias para poder ejecutar correctamente el Backend:

.. code-block:: text

    pip install -r requirements.txt
