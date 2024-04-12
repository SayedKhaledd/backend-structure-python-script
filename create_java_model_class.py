import os
import sys


# Function to create directory and file, then write the content
def write_file(directory, file_name, content):
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, file_name), "w") as file:
        file.write(content)
    print(f"{file_name} has been created in {directory}")


# Function to generate class contents for various components
def generate_class_content(package_name, class_name, template):
    return template.format(package=package_name, ClassName=class_name, className=class_name.lower())


# Function to get the directory for a given type
def get_directory(base_directory, type_path):
    return os.path.join(base_directory, *type_path.split('.'))


# Templates for different class types
templates = {
    "model": """package com.example.{package}.model;
import com.example.backendcoreservice.model.AbstractEntity;

public class {ClassName} extends AbstractEntity {{


}}
""",
    "dto": """package com.example.{package}.dto;
import com.example.backendcoreservice.dto.AbstractDto;

public class {ClassName}Dto extends AbstractDto {{


}}
""",
    "transformer/mapper": """package com.example.{package}.transformer.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.InjectionStrategy;
import com.example.{package}.dto.{ClassName}Dto;
import com.example.{package}.model.{ClassName};
import com.example.backendcoreservice.transformer.mapper.AbstractMapper;

@Mapper(componentModel = "spring", injectionStrategy = InjectionStrategy.CONSTRUCTOR)
public interface {ClassName}Mapper extends AbstractMapper<{ClassName}, {ClassName}Dto> {{


}}
""",
    "transformer": """package com.example.{package}.transformer;

import org.springframework.stereotype.Component;
import lombok.AllArgsConstructor;
import com.example.{package}.transformer.mapper.{ClassName}Mapper;
import com.example.{package}.dto.{ClassName}Dto;
import com.example.{package}.model.{ClassName};
import com.example.backendcoreservice.transformer.AbstractTransformer;

@Component
@AllArgsConstructor
public class {ClassName}Transformer implements AbstractTransformer<{ClassName}, {ClassName}Dto, {ClassName}Mapper> {{

    private final {ClassName}Mapper {className}Mapper;

    @Override
    public {ClassName}Mapper getMapper() {{
        return {className}Mapper;
    }}


}}
""",
    "dao/repo": """package com.example.{package}.dao.repo;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import com.example.{package}.model.{ClassName};

@Repository
public interface {ClassName}Repo extends JpaRepository<{ClassName}, Long> {{

}}
""",
    "dao": """package com.example.{package}.dao;

import com.example.{package}.model.{ClassName};
import com.example.backendcoreservice.dao.AbstractDao;
import com.example.{package}.dao.repo.{ClassName}Repo;

public interface {ClassName}Dao extends AbstractDao<{ClassName}, {ClassName}Repo> {{
    // Define additional DAO methods here
}}
""",
    "dao.impl": """package com.example.{package}.dao;

import org.springframework.stereotype.Component;
import lombok.AllArgsConstructor;
import com.example.{package}.dao.repo.{ClassName}Repo;

@Component
@AllArgsConstructor
public class {ClassName}DaoImpl implements {ClassName}Dao {{

    private final {ClassName}Repo {className}Repo;

    @Override
    public {ClassName}Repo getRepo() {{
        return {className}Repo;
    }}


}}
""",
    "service": """package com.example.{package}.service;

import com.example.{package}.model.{ClassName};
import com.example.{package}.dto.{ClassName}Dto;
import com.example.{package}.transformer.{ClassName}Transformer;
import com.example.{package}.dao.{ClassName}Dao;
import com.example.backendcoreservice.service.AbstractService;

public interface {ClassName}Service extends AbstractService<{ClassName}, {ClassName}Dto, {ClassName}Transformer, {ClassName}Dao> {{

}}
""",
    "service.impl": """package com.example.{package}.service;

import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import com.example.{package}.dao.{ClassName}Dao;
import com.example.{package}.transformer.{ClassName}Transformer;

@Slf4j
@Service
@AllArgsConstructor
public class {ClassName}ServiceImpl implements {ClassName}Service {{

    private final {ClassName}Dao {className}Dao;
    private final {ClassName}Transformer {className}Transformer;

    @Override
    public {ClassName}Dao getDao() {{
        return {className}Dao;
    }}

    @Override
    public {ClassName}Transformer getTransformer() {{
        return {className}Transformer;
    }}
    



}}
""",
    "controller": """package com.example.{package}.controller;

import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.example.{package}.dto.{ClassName}Dto;
import com.example.{package}.service.{ClassName}Service;
import com.example.backendcoreservice.controller.AbstractController;


@RestController
@RequestMapping("/api/{className}")
@AllArgsConstructor
public class {ClassName}Controller implements AbstractController<{ClassName}Service, {ClassName}Dto> {{

    private final {ClassName}Service {className}Service;


    @Override
    public {ClassName}Service getService() {{
        return {className}Service;
    }}





}}
"""
}


def create_class(class_name, base_directory, package_name, type_name):
    # Special handling for 'dao.impl' to avoid creating an 'impl' package
    if type_name == "dao.impl":
        directory = get_directory(base_directory, f"{package_name}.dao")
        file_name = f"{class_name}DaoImpl.java"

    elif type_name == "service.impl":
        directory = get_directory(base_directory, f"{package_name}.service")
        file_name = f"{class_name}ServiceImpl.java"
    elif type_name == "model":
        directory = get_directory(base_directory, f"{package_name}.model")
        file_name = f"{class_name}.java"
    else:
        directory = get_directory(base_directory, f"{package_name}.{type_name}")
        file_name = f"{class_name}{type_name.split('/')[-1].capitalize()}.java"

    content = generate_class_content(package_name, class_name, templates[type_name])
    write_file(directory, file_name, content)


def main():
    if len(sys.argv) != 3:
        print("Usage: python create_java_structure.py ClassName PackageName")
        sys.exit(1)

    class_name = sys.argv[1]
    package_name = sys.argv[2]
    base_directory = "src/main/java/com/example/"  # Assuming standard Maven project structure

    # Create each component
    for type_name in templates.keys():
        create_class(class_name, base_directory, package_name, type_name)

    # Any additional operations or function calls go here


if __name__ == "__main__":
    main()
