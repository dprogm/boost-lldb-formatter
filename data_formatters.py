import lldb

def stripped_type(type_ref: lldb.SBType) -> lldb.SBType:
  if type_ref.IsReferenceType():
    return type_ref.GetDereferencedType()
  return type_ref

class BoostOptionalSynthProvider:
  def __init__(self, valobj: lldb.SBValue, dict):
    self.valobj = valobj;

  def num_children(self):
    return 1
  def has_children(self):
    return True
  def get_child_index(self, name):
    return None

  def get_child_at_index(self, index):
    is_initialized: bool = (self.valobj.GetChildMemberWithName('m_initialized').GetValueAsUnsigned() == 1)
    if not is_initialized:
      return self.valobj.CreateValueFromExpression('val', '(const char*)"none"')
    this_type = stripped_type(self.valobj.GetType())
    value_type = this_type.GetTemplateArgumentType(0)
    return self.valobj.GetChildMemberWithName('m_storage').CreateChildAtOffset('val', 0, value_type)

  def update(self):
    pass

class BoostSmallVectorSynthProvider:
  def __init__(self, valobj: lldb.SBValue, dict):
    self.valobj = valobj;

  def num_children(self):
    return self.valobj.GetChildMemberWithName('m_holder').GetChildMemberWithName('m_size').GetValueAsUnsigned()
  def has_children(self):
    return True
  def get_child_index(self, name):
    return None

  def get_child_at_index(self, index):
    this_type = stripped_type(self.valobj.GetType())
    value_type: lldb.SBType = this_type.GetTemplateArgumentType(0)

    return (self.valobj.GetChildMemberWithName('m_holder').GetChildMemberWithName('m_start')
      .CreateChildAtOffset(f'[{index}]', index*value_type.GetByteSize(), value_type))

  def update(self):
    pass

class BoostVariantSyntheticChildrenProvider:

  def __init__(self, valobj: lldb.SBValue, internal_dict):
    self.valobj = valobj

  def num_children(self):
    return 1
  def has_children(self):
    return True
  def get_child_index(self, name):
    return None

  def get_child_at_index(self, index):
    type_idx = self.valobj.GetChildMemberWithName('which_').GetValueAsUnsigned()
    this_type = stripped_type(self.valobj.GetType())
    if type_idx >= this_type.GetNumberOfTemplateArguments():
      return self.valobj.CreateValueFromExpression('val', '(const char*)"uninitialized"')
    valueType: lldb.SBType = this_type.GetTemplateArgumentType(type_idx)
    value: lldb.SBValue = self.valobj.GetChildMemberWithName('storage_').Cast(valueType)
    return self.valobj.CreateValueFromData('val', value.GetData(), valueType)

  def update(self):
    pass

class BoostMultiIndexContainerSyntheticChildrenProvider:

  def __init__(self, valobj: lldb.SBValue, internal_dict):
    self.valobj = valobj

  def num_children(self):
    return self.valobj.GetChildMemberWithName('node_count').GetValueAsUnsigned()
  def has_children(self):
    return True
  def get_child_index(self, name):
    return None

  def get_child_at_index(self, index):
    this_type = stripped_type(self.valobj.GetType())
    value_type: lldb.SBType = this_type.GetTemplateArgumentType(0)
    return self.valobj.CreateValueFromExpression('val', '(const char*)"dummy"')

  def update(self):
    pass

def __lldb_init_module(debugger, internal_dict):
  debugger.HandleCommand('type synthetic add -l data_formatters.BoostOptionalSynthProvider -x "^boost::optional<.+>$"')
  debugger.HandleCommand('type synthetic add -l data_formatters.BoostSmallVectorSynthProvider -x "^boost::container::small_vector<.+>$"')
  debugger.HandleCommand('type synthetic add -l data_formatters.BoostVariantSyntheticChildrenProvider -x "^boost::variant<.+>$"')
  debugger.HandleCommand('type synthetic add -l data_formatters.BoostMultiIndexContainerSyntheticChildrenProvider -x "^boost::multi_index::multi_index_container<.+>$"')